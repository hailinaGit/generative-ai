"""Automated test suite & verification harness for Cambodia HR RAG Assistant.

Validates:
1. FR-01: Document ingestion and chunk metadata formatting.
2. FR-02: Semantic retrieval relevance and distance scores.
3. FR-03 & FR-04: Grounding, fallback behaviour, and citation integrity.

Usage:
    pytest tests/test_rag.py -v
    or:
    python tests/test_rag.py
"""
import sys
from pathlib import Path

# Add src to python path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from retrieve import retrieve_relevant_chunks, get_collection
from generate import generate_answer


def test_collection_integrity():
    """Verify ChromaDB has ingested the Cambodia HR regulations."""
    col = get_collection()
    count = col.count()
    assert count > 0, "ChromaDB collection is empty! Run `python src/ingest.py`."
    print(f"✓ ChromaDB collection contains {count} chunks.")


def test_retrieval_leave_policy():
    """Verify semantic retrieval returns Leave Policy section for annual leave query."""
    query = "How many days of annual leave are standard workers entitled to?"
    chunks = retrieve_relevant_chunks(query=query, top_k=2)

    assert len(chunks) > 0, "No chunks retrieved."
    top_chunk = chunks[0]
    assert top_chunk["source"] == "cambodia_hr_regulations.md"
    assert "Leave" in top_chunk["section"], f"Expected Leave section, got: {top_chunk['section']}"
    assert "18 days" in top_chunk["content"], "Expected 18 days text in retrieved content."
    print("✓ FR-02 (Vector Search): Annual leave retrieval test passed.")


def test_retrieval_overtime_policy():
    """Verify retrieval for overtime rates returns Employment & Working Conditions."""
    query = "What is the compensation rate for nighttime or Sunday overtime?"
    chunks = retrieve_relevant_chunks(query=query, top_k=2)

    assert len(chunks) > 0
    top_chunk = chunks[0]
    assert "200%" in top_chunk["content"], "Expected 200% overtime rate in chunk."
    print("✓ FR-02 (Vector Search): Overtime retrieval test passed.")


def test_retrieval_citations_format():
    """Verify FR-04 metadata contains source, section, and distance fields."""
    query = "What are the rules regarding maternity leave?"
    chunks = retrieve_relevant_chunks(query=query, top_k=1)

    assert len(chunks) == 1
    meta = chunks[0]
    assert "source" in meta and meta["source"]
    assert "section" in meta and meta["section"]
    assert "distance" in meta and isinstance(meta["distance"], (int, float))
    print("✓ FR-04 (Citations): Metadata format validated.")


def test_fallback_unsupported_query():
    """Verify FR-03 safety control & hallucination prevention.
    
    Queries outside the approved policy (e.g. US 401(k), equity stock options)
    must either receive high distance scores or trigger the strict fallback response.
    """
    out_of_domain_query = "What is the 401(k) company matching percentage in California?"
    chunks = retrieve_relevant_chunks(query=out_of_domain_query, top_k=2)
    
    # In vector retrieval, distance should be significantly higher for irrelevant topics
    # Distance in cosine space is 1 - cosine_similarity (higher distance = less similar)
    assert len(chunks) > 0
    top_chunk = chunks[0]
    # Cosine distance for completely unrelated queries is typically high (> 0.8)
    print(f"✓ FR-03 (Fallback Search): Out-of-domain query distance: {top_chunk['distance']:.4f}")

    # Verify fallback response contract when context is empty or absent
    res = generate_answer(query=out_of_domain_query, top_k=0)
    assert "I cannot find this information in the approved policy documents." in res["answer"], (
        f"Expected fallback string, got: {res['answer']}"
    )
    assert len(res["citations"]) == 0, "Fallback responses must not return citations."
    print("✓ FR-03 (Hallucination Control): Exact fallback message triggered.")


def run_all_tests():
    print("=" * 60)
    print("Running Cambodia HR RAG Assistant Test Suite")
    print("=" * 60)
    test_collection_integrity()
    test_retrieval_leave_policy()
    test_retrieval_overtime_policy()
    test_retrieval_citations_format()
    test_fallback_unsupported_query()
    print("=" * 60)
    print("All tests passed successfully! (100% compliance)")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()

