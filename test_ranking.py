"""Tests for the ranking engine."""

import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.ranking import compute_priority_scores, get_top_skills, filter_by_category


def test_priority_score_calculation():
    """Priority score for 30 mentions in 100 postings should be 30.0."""
    mention_df = pd.DataFrame({
        "canonical": ["FEA"],
        "mention_count": [30],
    })
    result = compute_priority_scores(mention_df, total_postings=100)
    assert result.iloc[0]["priority_score"] == 30.0


def test_ranking_order():
    """Skills should be sorted descending by priority score."""
    mention_df = pd.DataFrame({
        "canonical": ["A", "B", "C"],
        "mention_count": [10, 50, 30],
    })
    result = compute_priority_scores(mention_df, total_postings=100)
    scores = result["priority_score"].tolist()
    assert scores == sorted(scores, reverse=True)


def test_zero_mentions():
    """A skill with 0 mentions should have priority_score 0.0."""
    mention_df = pd.DataFrame({
        "canonical": ["Obscure Skill"],
        "mention_count": [0],
    })
    result = compute_priority_scores(mention_df, total_postings=100)
    assert result.iloc[0]["priority_score"] == 0.0


def test_get_top_skills():
    """get_top_skills(n=2) should return only 2 rows."""
    mention_df = pd.DataFrame({
        "canonical": ["A", "B", "C", "D"],
        "mention_count": [40, 30, 20, 10],
    })
    ranked = compute_priority_scores(mention_df, total_postings=100)
    top = get_top_skills(ranked, n=2)
    assert len(top) == 2
    assert top.iloc[0]["canonical"] == "A"


def test_filter_by_category():
    """Filtering by category should return only matching rows."""
    mention_df = pd.DataFrame({
        "canonical": ["SolidWorks", "FEA", "Python"],
        "mention_count": [50, 40, 30],
    })
    metadata = [
        {"canonical": "SolidWorks", "category": "cad"},
        {"canonical": "FEA", "category": "analysis"},
        {"canonical": "Python", "category": "programming"},
    ]
    ranked = compute_priority_scores(mention_df, 100, metadata)
    cad_only = filter_by_category(ranked, ["cad"])
    assert len(cad_only) == 1
    assert cad_only.iloc[0]["canonical"] == "SolidWorks"


def test_rank_column_starts_at_one():
    """Rank should start at 1, not 0."""
    mention_df = pd.DataFrame({
        "canonical": ["A", "B"],
        "mention_count": [50, 30],
    })
    ranked = compute_priority_scores(mention_df, 100)
    assert ranked.iloc[0]["rank"] == 1
    assert ranked.iloc[1]["rank"] == 2


if __name__ == "__main__":
    import traceback
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    passed = failed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS: {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {test.__name__}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed} passed, {failed} failed out of {passed + failed} tests")
