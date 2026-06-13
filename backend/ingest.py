"""Document ingestion pipeline for the Intelligent Slack Knowledge Base.

This module handles loading, chunking, embedding, and upserting documents
into the vector database. It supports PDFs, plain text files, and URLs.
"""

import os
import time
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    WebBaseLoader,
    Docx2txtLoader,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Load environment variables from root project directory
_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env_path = os.path.join(_base_dir, ".env")
if os.path.exists(_env_path):
    load_dotenv(dotenv_path=_env_path)
load_dotenv()


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Vector DB configuration: choose between "pinecone" and "chroma"
VECTOR_DB_PROVIDER = os.getenv("VECTOR_DB_PROVIDER", "chroma").lower()

# Pinecone settings
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "iskb")

# ChromaDB settings
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", os.path.join(_base_dir, "chroma_db"))

# Google Gemini embeddings
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


# ---------------------------------------------------------------------------
# Embedding model (initializer to avoid import overhead unless used)
# ---------------------------------------------------------------------------
class _BatchSafeEmbeddings:
    """Wrapper around GoogleGenerativeAIEmbeddings that forces batch_size=1.

    The default batch_size of 100 causes a Google API bug where only the first
    embedding is returned for the gemini-embedding-2 model. This wrapper ensures
    each text is embedded individually.
    """

    def __init__(self):
        from langchain_google_genai import GoogleGenerativeAIEmbeddings  # type: ignore

        try:
            # Try models/text-embedding-004 first (P2-T5 requirement)
            self._inner = GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
                google_api_key=GOOGLE_API_KEY,
                task_type="RETRIEVAL_DOCUMENT",
            )
            self._inner.embed_query("test")
        except Exception:
            # Fall back to models/gemini-embedding-2 if not supported
            self._inner = GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-2",
                google_api_key=GOOGLE_API_KEY,
                task_type="RETRIEVAL_DOCUMENT",
            )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed texts one at a time to avoid the multi-content API bug."""
        return [self._inner.embed_documents([t])[0] for t in texts]

    def embed_query(self, text: str) -> list[float]:
        """Delegate query embedding directly."""
        return self._inner.embed_query(text)


def _get_embeddings():
    """Lazy-load and return a batch-safe embeddings model."""
    return _BatchSafeEmbeddings()


# ---------------------------------------------------------------------------
# Text Splitter
# ---------------------------------------------------------------------------
def get_splitter() -> RecursiveCharacterTextSplitter:
    """Return a configured RecursiveCharacterTextSplitter."""
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )


# ---------------------------------------------------------------------------
# Document Loaders
# ---------------------------------------------------------------------------
def load_pdf(file_path: str) -> List[Any]:
    """Load a PDF document and return a list of pages as LangChain Documents."""
    loader = PyPDFLoader(file_path)
    return loader.load()


def load_txt(file_path: str) -> List[Any]:
    """Load a plain-text document and return a list containing one LangChain Document."""
    loader = TextLoader(file_path, encoding="utf-8")
    return loader.load()


def load_docx(file_path: str) -> List[Any]:
    """Load a DOCX document and return a list of LangChain Documents."""
    loader = Docx2txtLoader(file_path)
    return loader.load()


def load_url(url: str) -> List[Any]:
    """Load content from a URL and return a list of LangChain Documents."""
    loader = WebBaseLoader(url)
    return loader.load()


# ---------------------------------------------------------------------------
# Document ingestion helpers
# ---------------------------------------------------------------------------
def auto_tag(text: str) -> List[str]:
    """Use Gemini to extract 3 auto-tags from the text."""
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0, google_api_key=GOOGLE_API_KEY)
        prompt = PromptTemplate.from_template(
            "Extract exactly 3 concise tag words that categorize the following text. "
            "Return them as a comma-separated list. Text: {text}"
        )
        chain = prompt | llm
        result = chain.invoke({"text": text[:2000]}) # Use first 2000 chars
        content = result.content if hasattr(result, "content") else result
        if isinstance(content, list):
            content = " ".join([str(c) for c in content])
        elif not isinstance(content, str):
            content = str(content)
        tags = [t.strip() for t in content.split(",") if t.strip()]
        return tags[:3]
    except Exception as e:
        print(f"Auto-tagging failed: {e}")
        return ["untagged"]


def add_metadata(chunks: List[Any], source: str, scope: str = "org", tags: List[str] = None) -> List[Any]:
    """Inject standard metadata into every chunk."""
    for chunk in chunks:
        chunk.metadata.update({
            "source": source,
            "scope": scope,
            "timestamp": time.time(),
            "tags": tags or ["untagged"]
        })
    return chunks


def process_file(file_path: str, scope: str = "org") -> List[Any]:
    """
    Load a file, split into chunks, and inject metadata.
    Returns a list of LangChain Document chunks.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        docs = load_pdf(str(path))
    elif suffix == ".txt":
        docs = load_txt(str(path))
    elif suffix == ".docx":
        docs = load_docx(str(path))
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    # Split documents into chunks
    splitter = get_splitter()
    chunks = splitter.split_documents(docs)

    # Auto tag
    full_text = "\n".join([d.page_content for d in docs])
    tags = auto_tag(full_text)

    # Inject metadata
    add_metadata(chunks, source=path.name, scope=scope, tags=tags)
    return chunks


def process_url(url: str, scope: str = "org") -> List[Any]:
    """
    Load content from a URL, split into chunks, and inject metadata.
    Returns a list of LangChain Document chunks.
    """
    docs = load_url(url)
    splitter = get_splitter()
    chunks = splitter.split_documents(docs)
    
    # Auto tag
    full_text = "\n".join([d.page_content for d in docs])
    tags = auto_tag(full_text)
    
    add_metadata(chunks, source=url, scope=scope, tags=tags)
    return chunks


# ---------------------------------------------------------------------------
# Vector DB helpers
# ---------------------------------------------------------------------------
def _get_pinecone_store():
    """Return a Pinecone vector store wrapper (requires pinecone-client + langchain-pinecone)."""
    from langchain_pinecone import PineconeVectorStore  # type: ignore # noqa: F401
    from pinecone import Pinecone  # type: ignore

    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
    embeddings = _get_embeddings()
    return PineconeVectorStore(index=index, embedding=embeddings)


def _get_chroma_store():
    """Return a local ChromaDB vector store wrapper."""
    import chromadb
    from chromadb.config import Settings
    from langchain_chroma import Chroma  # type: ignore

    embeddings = _get_embeddings()
    # Use a persistent client with check_same_thread=False to avoid SQLite threading errors
    chroma_client = chromadb.PersistentClient(
        path=CHROMA_PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False),
    )
    return Chroma(
        client=chroma_client,
        embedding_function=embeddings,
    )


def get_vector_store():
    """Return the configured vector store (Pinecone or ChromaDB)."""
    if VECTOR_DB_PROVIDER == "pinecone":
        try:
            return _get_pinecone_store()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Pinecone: {e}")
    return _get_chroma_store()


# ---------------------------------------------------------------------------
# Upsert pipeline
# ---------------------------------------------------------------------------
def upsert_chunks(chunks: List[Any], metadata: Dict[str, Any] = None) -> int:
    """
    Embed and upsert a list of LangChain Document chunks into the vector DB.

    Args:
        chunks: List of LangChain Document objects.
        metadata: Optional additional metadata to attach to every chunk.

    Returns:
        Number of chunks successfully upserted.
    """
    if not chunks:
        return 0

    # Merge any extra metadata
    if metadata:
        for chunk in chunks:
            chunk.metadata.update(metadata)

    store = get_vector_store()
    store.add_documents(chunks)

    return len(chunks)


def upsert_file(file_path: str, scope: str = "org", extra_metadata: Dict[str, Any] = None) -> int:
    """
    Convenience wrapper: load, chunk, and upsert a single file.

    Returns:
        Number of chunks upserted.
    """
    chunks = process_file(file_path, scope=scope)
    return upsert_chunks(chunks, metadata=extra_metadata)


def upsert_url(url: str, scope: str = "org", extra_metadata: Dict[str, Any] = None) -> int:
    """
    Convenience wrapper: load, chunk, and upsert content from a URL.

    Returns:
        Number of chunks upserted.
    """
    chunks = process_url(url, scope=scope)
    return upsert_chunks(chunks, metadata=extra_metadata)


# ---------------------------------------------------------------------------
# Retrieval helpers
# ---------------------------------------------------------------------------
def get_all_documents() -> List[Dict[str, Any]]:
    """
    Retrieve all unique source names and metadata from the vector DB.

    Returns:
        List of dicts with keys: source, scope, timestamp
    """
    store = get_vector_store()

    # ChromaDB implementation
    if VECTOR_DB_PROVIDER == "chroma":
        data = store.get(include=["metadatas"])
        metas = data.get("metadatas", []) if data else []
        seen = set()
        results = []
        for meta in metas:
            if not meta:
                continue
            source = meta.get("source")
            if source and source not in seen:
                seen.add(source)
                results.append({
                    "source": source,
                    "scope": meta.get("scope", "org"),
                    "timestamp": meta.get("timestamp"),
                    "tags": meta.get("tags", ["untagged"]),
                })
        return results

    # Pinecone: fallback to a broad similarity search
    # (Pinecone serverless doesn't expose direct record listing easily)
    results = store.similarity_search("", k=10000)
    seen = set()
    docs = []
    for doc in results:
        source = doc.metadata.get("source")
        if source and source not in seen:
            seen.add(source)
            docs.append({
                "source": source,
                "scope": doc.metadata.get("scope", "org"),
                "timestamp": doc.metadata.get("timestamp"),
                "tags": doc.metadata.get("tags", ["untagged"]),
            })
    return docs

if __name__ == "__main__":
    # Quick sanity check
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("This is a test document for the ingestion pipeline.")
        temp_path = f.name

    chunks = process_file(temp_path, scope="org")
    print(f"Processed {len(chunks)} chunks from {temp_path}")
    for chunk in chunks:
        print(chunk.metadata)