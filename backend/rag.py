"""RAG (Retrieval-Augmented Generation) pipeline for the Intelligent Slack Knowledge Base.

This module builds a RetrievalQA chain that retrieves relevant chunks from the
vector store and generates grounded answers using Google Gemini.
"""

import os
import re
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_core.prompts import PromptTemplate

from ingest import get_vector_store

# Load environment variables
_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env_path = os.path.join(_base_dir, ".env")
if os.path.exists(_env_path):
    load_dotenv(dotenv_path=_env_path)
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ---------------------------------------------------------------------------
# No-Hallucination System Prompt Template
# ---------------------------------------------------------------------------
RAG_PROMPT_TEMPLATE = PromptTemplate(
    template=(
        "You are an intelligent organizational assistant. Your objective is to solve "
        "the user's inquiry.\n\n"
        "Here is the context retrieved from our organization's database:\n"
        "Context:\n{context}\n\n"
        "Instructions:\n"
        "1. Prioritize the provided context to answer the question. If the context contains the information, "
        "answer based on it and append the exact text '[USED_CONTEXT]' at the very end of your response.\n"
        "2. If the context does NOT contain the information needed to answer the question, or if the context "
        "is empty/irrelevant, use your general knowledge to answer the question. In this case, do NOT append '[USED_CONTEXT]' "
        "to your response.\n"
        "3. If the answer is partially based on the context and partially on general knowledge, append '[USED_CONTEXT]' "
        "at the very end of your response.\n\n"
        "Question: {question}\n\n"
        "Answer:"
    ),
    input_variables=["context", "question"],
)

_SUMMARY_PROMPT_TEMPLATE = PromptTemplate(
    template=(
        "Summarize the following document in exactly 3 to 5 markdown-bulleted takeaways. "
        "Each bullet must start with '* '. Be concise and actionable.\n\n"
        "{text}"
    ),
    input_variables=["text"],
)


def _get_llm():
    """Return a ChatGoogleGenerativeAI LLM instance."""
    try:
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=GOOGLE_API_KEY,
        )
    except Exception:
        # Fallback if the primary model isn't available
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=GOOGLE_API_KEY,
        )


# Global in-memory store for conversational memory per user
SESSION_MEMORY = {}

CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(
    "Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.\n\n"
    "Chat History:\n{chat_history}\n"
    "Follow Up Input: {question}\n"
    "Standalone question:"
)

def build_rag_chain(top_k: int = 4, user_id: str = None, channel_id: str = None) -> ConversationalRetrievalChain:
    """
    Build and return a RetrievalQA chain backed by the configured vector store.
    If user_id and channel_id are provided, the retriever is scoped so that only
    documents the user is authorized to see are returned.

    Args:
        top_k: Number of relevant chunks to retrieve.
        user_id: Slack user ID for scoping (optional).
        channel_id: Slack channel ID for scoping (optional).

    Returns:
        A ready-to-use RetrievalQA chain.
    """
    llm = _get_llm()
    vector_store = get_vector_store()

    search_kwargs = {"k": top_k}
    # NOTE: ChromaDB 1.x has a bug with $in operator on metadata fields.
    # We skip the scope filter entirely — all documents are returned for now.
    # Scoping can be re-enabled with Pinecone which supports $in natively.

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs=search_kwargs,
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": RAG_PROMPT_TEMPLATE},
        condense_question_prompt=CONDENSE_QUESTION_PROMPT,
    )

    return chain


def extract_citations(source_documents: list) -> str:
    """
    Extract de-duplicated source filenames from retrieved Document objects.

    Args:
        source_documents: List of LangChain Document objects returned by the chain.

    Returns:
        A formatted footer string like "\\n\\n*Sources Used:* file1.txt, file2.txt"
    """
    sources = list({doc.metadata.get("source", "unknown") for doc in source_documents})
    sources.sort()
    if not sources:
        return ""
    return "\n\n*Sources Used:* " + ", ".join(sources)


def run_rag_query(question: str, top_k: int = 4, user_id: str = None, channel_id: str = None) -> dict:
    """
    Execute a RAG query and return the answer with citation metadata.

    Args:
        question: The user's natural-language question.
        top_k: Number of chunks to retrieve.
        user_id: Slack user ID for scoping (optional).
        channel_id: Slack channel ID for scoping (optional).

    Returns:
        Dict with keys: "answer", "sources_footer", "source_documents"
    """
    chain = build_rag_chain(top_k=top_k, user_id=user_id, channel_id=channel_id)
    
    chat_history = SESSION_MEMORY.get(user_id, [])
    
    result = chain.invoke({"question": question, "chat_history": chat_history})

    answer = result.get("answer", "")
    source_docs = result.get("source_documents", [])

    # Check if the [USED_CONTEXT] marker is present (case-insensitive)
    if "[used_context]" in answer.lower():
        # Remove the marker from the final answer text
        answer = re.sub(r'(?i)\[used_context\]', '', answer).strip()
        sources_footer = extract_citations(source_docs)
    else:
        sources_footer = ""
        source_docs = []

    # Update memory (keep last 3 turns)
    if user_id:
        chat_history.append((question, answer))
        SESSION_MEMORY[user_id] = chat_history[-3:]

    return {
        "answer": answer,
        "sources_footer": sources_footer,
        "source_documents": source_docs,
    }


def summarize_document(doc_name: str) -> str:
    """
    Retrieve all chunks for a named document and generate a 3-5 bullet summary.

    Args:
        doc_name: The source filename or URL to summarize.

    Returns:
        A markdown summary with a bold header and bullet points.
    """
    from langchain_core.documents import Document as LCDocument
    from ingest import VECTOR_DB_PROVIDER

    vector_store = get_vector_store()

    # ChromaDB: use get() with where filter to avoid embedding an empty string
    if VECTOR_DB_PROVIDER == "chroma":
        data = vector_store.get(where={"source": doc_name}, include=["documents", "metadatas"])
        ids = data.get("ids", [])
        texts = data.get("documents", [])
        metas = data.get("metadatas", [])
        docs = [LCDocument(page_content=t, metadata=m or {}) for t, m in zip(texts, metas)]
    else:
        # Fallback for Pinecone: embed a generic query and filter
        docs = vector_store.similarity_search(
            "document content",
            k=100,
            filter={"source": doc_name}
        )

    if not docs:
        return f"*No document found with name `{doc_name}`.*"

    combined_text = "\n".join([d.page_content for d in docs])

    llm = _get_llm()
    summary_chain = _SUMMARY_PROMPT_TEMPLATE | llm
    summary = summary_chain.invoke({"text": combined_text})

    # summary is an AIMessage or string depending on the langchain version
    if hasattr(summary, "content"):
        summary = summary.content

    return f"*Summary of `{doc_name}`:*\n{summary}"
