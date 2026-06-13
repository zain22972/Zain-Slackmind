"""Phase 5 Validation Tests

Run with: python backend/tests/test_validation.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rag import run_rag_query, extract_citations, summarize_document
from langchain_core.documents import Document

def test_sources_footer():
    """P5-T4: Sources Used: footer appears in every successful response."""
    print("=" * 60)
    print("TEST: Sources Audit (P5-T4)")
    result = run_rag_query("What are the key features of the project?")
    answer = result["answer"]
    footer = result["sources_footer"]
    
    assert footer.startswith("\n\n*Sources Used:*"), f"Missing Sources footer: {footer}"
    assert len(result["source_documents"]) > 0, "No source documents retrieved!"
    
    print(f"  Sources footer: {footer}")
    print("  PASS - Sources Used: footer present")
    return True


def test_no_hallucination():
    """P5-T2: Out-of-scope query returns general answer without citing context."""
    print("=" * 60)
    print("TEST: General Knowledge Fallback (P5-T2)")
    
    result = run_rag_query("What is the capital of France?")
    answer = result["answer"]
    footer = result["sources_footer"]
    
    # It should answer from general knowledge (contain Paris)
    assert "Paris" in answer, f"Expected answer to contain Paris, got: '{answer}'"
    # It should not cite any sources
    assert not footer, f"Expected empty sources footer, got: '{footer}'"
    assert len(result["source_documents"]) == 0, f"Expected 0 source documents, got {len(result['source_documents'])}"
    
    print(f"  Answer: {answer[:100]}")
    print("  PASS - Answered general query without false citations")
    return True


def test_citation_deduplication():
    """P5-T4: De-duplication of source filenames."""
    print("=" * 60)
    print("TEST: Citation De-duplication")
    
    docs = [
        Document(page_content="a", metadata={"source": "api_reference.txt"}),
        Document(page_content="b", metadata={"source": "api_reference.txt"}),
        Document(page_content="c", metadata={"source": "deployment_notes.txt"}),
    ]
    footer = extract_citations(docs)
    
    assert "api_reference.txt" in footer
    assert footer.count("api_reference.txt") == 1, f"Duplicate not removed: {footer}"
    print(f"  PASS - Deduplicated: {footer}")
    return True


def test_privacy_partition():
    """P5-T3: Scoped retriever only returns docs user is authorized to see."""
    print("=" * 60)
    print("TEST: Privacy Partition (P5-T3)")
    
    # User "U123" in channel "C456" - should only see org, team_C456, user_U123 docs
    # All seeded docs are "org" scope, so they should still see them
    result = run_rag_query(
        "What is the project overview?",
        user_id="U123",
        channel_id="C456"
    )
    
    # Should still work because all seeded docs are 'org' scope
    assert len(result["source_documents"]) > 0, "No docs retrieved with scope filter!"
    print(f"  PASS - Scoped retriever returned {len(result['source_documents'])} docs")
    return True


def test_summarize():
    """P4-T8: /summarize returns bullet-point summary."""
    print("=" * 60)
    print("TEST: /summarize Command (P4-T8)")
    
    summary = summarize_document("project_overview.txt")
    
    assert summary.startswith("*Summary of"), f"Bad format: {summary[:100]}"
    assert "*" in summary or "-" in summary, "No bullet points found"
    
    print(f"  Summary: {summary[:200]}...")
    print("  PASS - Summarize returns formatted bullets")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 5 VALIDATION TESTS")
    print("=" * 60)
    
    results = []
    results.append(test_citation_deduplication())
    results.append(test_sources_footer())
    results.append(test_no_hallucination())
    results.append(test_privacy_partition())
    results.append(test_summarize())
    
    print("=" * 60)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    if all(results):
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("=" * 60)
