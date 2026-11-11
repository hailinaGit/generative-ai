"""Semantic retrieval module for Cambodia HR & Policy Knowledge Assistant (FR-02).

Usage:
    python src/retrieve.py "How many days of annual leave are employees entitled to?"
    python src/retrieve.py --query "What is the overtime rate on public holidays?" --top-k 3
"""
import argparse
import sys
from pathlib import Path
from typing import Any

import chromadb

COLLECTION_NAME = "policies"
DEFAULT_DB_DIR = "chroma_db"


def get_collection(db_dir: str = DEFAULT_DB_DIR):
    """Load persistent ChromaDB client and retrieve the policies collection."""
    db_path = Path(db_dir)
    if not db_path.exists():
        raise FileNotFoundError(
            f"ChromaDB directory '{db_dir}' not found. Please run `python src/ingest.py` first."
        )
    client = chromadb.PersistentClient(path=str(db_path))
    return client.get_collection(COLLECTION_NAME)


def retrieve_relevant_chunks(
    query: str,
    top_k: int = 3,
    db_dir: str = DEFAULT_DB_DIR
) -> list[dict[str, Any]]:
    """Query ChromaDB and return a structured list of retrieved chunks with citations."""
    if top_k <= 0:
        return []

    col = get_collection(db_dir)
    results = col.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    if not results or not results.get("documents") or not results.get("metadatas") or not results.get("distances"):
        return chunks

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    for doc, meta, dist in zip(docs, metas, distances):
        chunks.append({
            "content": doc,
            "source": meta.get("source", "unknown"),
            "section": meta.get("section", "unknown"),
            "chunk_index": meta.get("chunk_index", 0),
            "distance": round(dist, 4)
        })

    return chunks


def format_context_for_prompt(chunks: list[dict[str, Any]]) -> str:
    """Format retrieved chunks into a prompt-ready context string with citations."""
    if not chunks:
        return "No relevant context found."

    context_blocks = []
    for i, c in enumerate(chunks, 1):
        block = (
            f"--- Context Block {i} ---\n"
            f"Source Document: {c['source']}\n"
            f"Section: {c['section']}\n"
            f"Content:\n{c['content']}\n"
        )
        context_blocks.append(block)
    return "\n".join(context_blocks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query_pos", nargs="?", help="Search query as positional argument")
    parser.add_argument("--query", "-q", help="Search query string")
    parser.add_argument("--top-k", "-k", type=int, default=3, help="Number of chunks to return")
    parser.add_argument("--db-dir", default=DEFAULT_DB_DIR, help="Path to chroma_db storage")
    args = parser.parse_args()

    query = args.query or args.query_pos
    if not query:
        print("Error: Please provide a query to search.")
        print("Example: python src/retrieve.py 'What are the maternity leave rules?'")
        sys.exit(1)

    try:
        chunks = retrieve_relevant_chunks(query, top_k=args.top_k, db_dir=args.db_dir)
    except Exception as e:
        print(f"Retrieval error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\nQuery: \"{query}\"")
    print(f"Retrieved {len(chunks)} relevant chunk(s):\n")

    for i, c in enumerate(chunks, 1):
        print(f"[{i}] {c['source']} -> Section: \"{c['section']}\" (Cosine distance: {c['distance']})")
        print(f"{c['content']}")
        print("-" * 60)


if __name__ == "__main__":
    main()

