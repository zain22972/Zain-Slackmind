"""Batch seed script for the Intelligent Slack Knowledge Base.

Reads all files from a ./test_docs/ folder, runs each through the
ingestion pipeline, and reports progress.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Resolve paths relative to this script's location
_BASE_DIR = Path(__file__).resolve().parent.parent

# Allow importing ingest.py
sys.path.insert(0, str(_BASE_DIR / "backend"))

from ingest import upsert_file, get_all_documents

# Load environment variables from root .env if present
_env_path = _BASE_DIR / ".env"
if _env_path.exists():
    load_dotenv(dotenv_path=str(_env_path))
load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TEST_DOCS_DIR = _BASE_DIR / "test_docs"


def seed_documents(docs_dir: Path) -> tuple[int, int]:
    """
    Load all supported documents from *docs_dir*, chunk and upsert them.

    Returns:
        (total_chunks_upserted, total_documents_processed)
    """
    if not docs_dir.exists():
        raise FileNotFoundError(f"Documents directory not found: {docs_dir.resolve()}")

    supported_extensions = {".pdf", ".txt"}
    files = sorted([f for f in docs_dir.iterdir() if f.is_file() and f.suffix.lower() in supported_extensions])

    if not files:
        print(f"No supported documents found in {docs_dir.resolve()}")
        return 0, 0

    total_chunks = 0
    total_docs = 0

    for file_path in files:
        print(f"Processing: {file_path.name} ... ", end="", flush=True)
        try:
            count = upsert_file(str(file_path), scope="org")
            total_chunks += count
            total_docs += 1
            print(f"upserted {count} chunks")
        except Exception as exc:  # noqa: BLE001
            print(f"FAILED ({exc})")

    return total_chunks, total_docs


def main() -> None:
    chunks, docs = seed_documents(TEST_DOCS_DIR)
    print(f"\n{'=' * 50}")
    print(f"Upserted {chunks} chunks from {docs} documents")
    print(f"{'=' * 50}")

    # Optional: list all unique sources
    sources = get_all_documents()
    if sources:
        print("\nIndexed sources:")
        for s in sources:
            print(f"  - {s['source']} (scope: {s['scope']})")


if __name__ == "__main__":
    main()