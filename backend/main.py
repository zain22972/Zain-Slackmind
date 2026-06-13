import os
import sys
import tempfile
from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler

# Ensure backend directory is on the path for local imports
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from ingest import upsert_file, get_all_documents, upsert_url
from rag import run_rag_query, summarize_document
from pydantic import BaseModel

# Load local environment variables from root directory if they exist
load_dotenv(dotenv_path="../.env")
load_dotenv()

app = FastAPI(title="Intelligent Slack Knowledge Base API")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:5174",
        "http://localhost:3000", 
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Slack Bolt App
slack_app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)
handler = SlackRequestHandler(slack_app)


# ---------------------------------------------------------------------------
# Slack app_mention handler — RAG-powered responses (with security scoping)
# ---------------------------------------------------------------------------
@slack_app.event("app_mention")
def handle_app_mention(event, say):
    """Handle @bot mentions: strip the mention, run RAG with scope filter, respond with citations."""
    # Strip the bot user mention tag from the message text
    user_text = event.get("text", "").split(">", 1)[-1].strip()

    if not user_text:
        say(text="Please ask a question after mentioning me.", thread_ts=event.get("ts"))
        return

    user_id = event.get("user")
    channel_id = event.get("channel")

    # Run the RAG pipeline in a fresh thread to avoid SQLite cross-thread errors
    import concurrent.futures
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_rag_query, user_text, 4, user_id, channel_id)
            result = future.result(timeout=60)
    except Exception as exc:
        say(
            text=f"Sorry, an error occurred while processing your question: {exc}",
            thread_ts=event.get("ts"),
        )
        return

    # Build the final response with citations
    full_response = result["answer"] + result["sources_footer"]

    say(text=full_response, thread_ts=event.get("ts"))


# ---------------------------------------------------------------------------
# Slack /summarize slash command
# ---------------------------------------------------------------------------
@slack_app.command("/summarize")
def handle_summarize(ack, command, say):
    """Handle /summarize <doc_name> -- fetch doc chunks and return bullet-point summary."""
    ack()

    doc_name = command.get("text", "").strip()
    if not doc_name:
        say("Usage: `/summarize <document_name>`")
        return

    try:
        summary = summarize_document(doc_name)
    except Exception as exc:
        say(f"Sorry, I couldn't summarize `{doc_name}`. Error: {exc}")
        return

    say(summary)

# ---------------------------------------------------------------------------
# Slack /ingest-url slash command
# ---------------------------------------------------------------------------
@slack_app.command("/ingest-url")
def handle_ingest_url(ack, command, say):
    """Handle /ingest-url <url>"""
    ack()
    url = command.get("text", "").strip()
    if not url.startswith("http"):
        say("Usage: `/ingest-url <http_url>`")
        return
    channel = command.get("channel_id", "general")
    try:
        chunks = upsert_url(url, scope=f"team_{channel}")
        say(f"Successfully ingested {url} ({chunks} chunks) into scope team_{channel}")
    except Exception as exc:
        say(f"Failed to ingest URL: {exc}")

# ---------------------------------------------------------------------------
# Slack /ingest-thread slash command
# ---------------------------------------------------------------------------
@slack_app.command("/ingest-thread")
def handle_ingest_thread(ack, command, say, client):
    """Handle /ingest-thread <thread_ts>"""
    ack()
    text = command.get("text", "").strip()
    if not text:
        say("Usage: `/ingest-thread <thread_ts>`")
        return
    try:
        channel_id = command.get("channel_id")
        result = client.conversations_replies(channel=channel_id, ts=text)
        messages = result.get("messages", [])
        if not messages:
            say("No messages found in thread.")
            return
            
        thread_text = "\n".join([f"{m.get('user', 'User')}: {m.get('text', '')}" for m in messages])
        
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt", encoding="utf-8") as f:
            f.write(thread_text)
            tmp_path = f.name
            
        chunks = upsert_file(tmp_path, scope=f"team_{channel_id}", extra_metadata={"source": f"Slack Thread {text}"})
        os.unlink(tmp_path)
        
        say(f"Successfully ingested thread {text} ({chunks} chunks).")
    except Exception as exc:
        say(f"Failed to ingest thread: {exc}")


@app.post("/slack/events")
async def slack_events(request: Request):
    # Retrieve request body
    try:
        body = await request.json()
    except Exception:
        body = {}

    # Check if it is a Slack URL verification challenge
    if body.get("type") == "url_verification":
        return JSONResponse(content={"challenge": body.get("challenge")})

    # Otherwise, pass the request to the Bolt handler
    return await handler.handle(request)

@app.get("/")
async def root():
    return {
        "message": "Intelligent Slack Knowledge Base API is running",
        "endpoints": {
            "health": "/health",
            "slack_events": "/slack/events",
            "documents": "/api/documents",
            "upload": "/api/documents/upload"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# ---------------------------------------------------------------------------
# Document ingestion endpoints
# ---------------------------------------------------------------------------

SUPPORTED_UPLOAD_EXTENSIONS = {".pdf", ".txt", ".docx"}

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    scope: str = Form("org"),
):
    """
    Upload a document (PDF, TXT, DOCX), ingest it into the vector database.

    Returns:
        JSON with status, document name, and chunk count.
    """
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_UPLOAD_EXTENSIONS:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": f"Unsupported file type '{suffix}'. Supported: {', '.join(SUPPORTED_UPLOAD_EXTENSIONS)}"
            }
        )

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        chunk_count = upsert_file(tmp_path, scope=scope, extra_metadata={"source": file.filename})
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(exc)}
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    return {
        "status": "indexed",
        "document": file.filename,
        "chunks": chunk_count,
    }


class UrlPayload(BaseModel):
    url: str
    scope: str = "org"

class QueryPayload(BaseModel):
    question: str
    conversation_history: list = []
    user_id: str = "web_user"
    channel_id: str = "web_channel"

@app.post("/api/query")
async def api_query(payload: QueryPayload):
    """
    Query the knowledge base using the RAG pipeline.
    """
    try:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                run_rag_query, 
                payload.question, 
                4, 
                payload.user_id, 
                payload.channel_id
            )
            result = future.result(timeout=60)
        
        seen_sources = set()
        sources = []
        for doc in result.get("source_documents", []):
            src_name = doc.metadata.get("source", "unknown")
            if src_name not in seen_sources:
                seen_sources.add(src_name)
                tags_val = doc.metadata.get("tags")
                if isinstance(tags_val, list):
                    tags_str = ", ".join(tags_val)
                elif isinstance(tags_val, str):
                    tags_str = tags_val
                else:
                    tags_str = "untagged"
                sources.append({
                    "source": src_name,
                    "tags": tags_str
                })
            
        return {
            "answer": result["answer"],
            "sources": sources
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(exc)}
        )

@app.post("/api/documents/url")
async def upload_url(payload: UrlPayload):
    """
    Ingest a document from a URL.
    """
    try:
        chunk_count = upsert_url(payload.url, scope=payload.scope)
        return {
            "status": "indexed",
            "document": payload.url,
            "chunks": chunk_count,
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(exc)})


@app.get("/api/documents")
async def list_documents():
    """
    List all unique indexed documents.

    Returns:
        JSON list of documents with source, scope, and timestamp metadata.
    """
    try:
        docs = get_all_documents()
        return docs
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(exc)}
        )
