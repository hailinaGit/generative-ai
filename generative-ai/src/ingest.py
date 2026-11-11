"""Ingest, clean, chunk and store policy documents in ChromaDB (FR-01).

Usage (from rag-knowledge-assistant/):
    python src/ingest.py --data-dir data/raw --db-dir chroma_db --reset

Embeddings use Chroma's default local model (all-MiniLM-L6-v2), so no API key
is needed. Collection uses cosine distance (FR-02).
"""
import argparse
import hashlib
import re
from pathlib import Path

import chromadb

COLLECTION = "policies"


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def load_sections(path: Path) -> list[tuple[str, str]]:
    """Return (section_title, text) pairs for a .md/.txt/.pdf file."""
    if path.suffix.lower() == ".pdf":
        
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        return [
            (f"Page {i}", clean_text(p.extract_text() or ""))
            for i, p in enumerate(reader.pages, 1)
        ]
    text = clean_text(path.read_text(encoding="utf-8"))
    sections, title, buf = [], path.stem, []
    for line in text.split("\n"):
        m = re.match(r"^#{1,6}\s+(.*)", line)
        if m:
            if "".join(buf).strip():
                sections.append((title, "\n".join(buf).strip()))
            title, buf = m.group(1).strip(), []
        else:
            buf.append(line)
    if "".join(buf).strip():
        sections.append((title, "\n".join(buf).strip()))
    return sections


def chunk_text(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    """Split text into ~size-char chunks with overlap, preferring word boundaries."""
    if len(text) <= size:
        return [text] if text else []
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            space = text.rfind(" ", start + size // 2, end)
            end = space if space != -1 else end
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return [c for c in chunks if c]


def build_records(data_dir: Path, size: int, overlap: int):
    ids, docs, metas = [], [], []
    files = sorted(p for p in data_dir.rglob("*") if p.suffix.lower() in {".md", ".txt", ".pdf"})
    for path in files:
        for title, body in load_sections(path):
            for i, chunk in enumerate(chunk_text(body, size, overlap)):
                key = f"{path.name}|{title}|{i}|{chunk}"
                ids.append(hashlib.sha1(key.encode()).hexdigest())
                docs.append(chunk)
                metas.append({"source": path.name, "section": title, "chunk_index": i})
    return files, ids, docs, metas


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", default="data/raw")
    ap.add_argument("--db-dir", default="chroma_db")
    ap.add_argument("--chunk-size", type=int, default=800)
    ap.add_argument("--chunk-overlap", type=int, default=100)
    ap.add_argument("--reset", action="store_true", help="drop existing collection first")
    args = ap.parse_args()

    files, ids, docs, metas = build_records(Path(args.data_dir), args.chunk_size, args.chunk_overlap)
    if not docs:
        raise SystemExit(f"No ingestible documents found in {args.data_dir}")

    client = chromadb.PersistentClient(path=args.db_dir)
    if args.reset:
        try:
            client.delete_collection(COLLECTION)
        except Exception:
            pass
    col = client.get_or_create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})
    col.upsert(ids=ids, documents=docs, metadatas=metas)
    print(f"Ingested {len(files)} files -> {len(docs)} chunks (collection total: {col.count()})")


if __name__ == "__main__":
    main()

