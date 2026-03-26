"""Tests for skills gap analysis."""

import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.gap_analysis import analyze_gap, compute_gap_score
from engine.keyword_extractor import build_regex_patterns


def _make_ranked_df():
    """Create a sample ranked DataFrame for testing."""
    return pd.DataFrame({
        "rank": [1, 2, 3, 4, 5],
        "canonical": ["SolidWorks", "FEA", "Python", "GD&T", "MATLAB"],
        "category": ["cad", "analysis", "programming", "standards", "analysis"],
        "mention_count": [60, 50, 40, 35, 30],
        "priority_score": [80.0, 66.7, 53.3, 46.7, 40.0],
    })


def _make_patterns():
    """Create patterns for the 5 test skills."""
    skills = [
        {"canonical": "SolidWorks", "aliases": ["SolidWorks"], "category": "cad", "industries": []},
        {"canonical": "FEA", "aliases": ["FEA", "Finite Element Analysis"], "category": "analysis", "industries": []},
        {"canonical": "Python", "aliases": ["Python"], "category": "programming", "industries": []},
        {"canonical": "GD&T", "aliases": ["GD&T"], "category": "standards", "industries": []},
        {"canonical": "MATLAB", "aliases": ["MATLAB"], "category": "analysis", "industries": []},
    ]
    return build_regex_patterns(skills)


def test_all_skills_present():
    """Resume with all skills should have empty missing list."""
    ranked = _make_ranked_df()
    patterns = _make_patterns()
    resume = "I have experience with SolidWorks, FEA, Python, GD&T, and MATLAB."
    present, missing = analyze_gap(resume, ranked, patterns, top_n=5)
    assert len(present) == 5
    assert len(missing) == 0


def test_no_skills_present():
    """Empty resume should have all skills missing."""
    ranked = _make_ranked_df()
    patterns = _make_patterns()
    resume = ""
    present, missing = analyze_gap(resume, ranked, patterns, top_n=5)
    assert len(present) == 0
    assert len(missing) == 5


def test_partial_coverage():
    """Resume with some skills should split correctly."""
    ranked = _make_ranked_df()
    patterns = _make_patterns()
    resume = "Proficient in SolidWorks and Python."
    present, missing = analyze_gap(resume, ranked, patterns, top_n=5)
    assert len(present) == 2
    assert len(missing) == 3
    present_names = {s["canonical"] for s in present}
    assert present_names == {"SolidWorks", "Python"}


def test_gap_score_full():
    """100% coverage."""
    assert compute_gap_score([1, 2, 3], []) == 100.0


def test_gap_score_empty():
    """0% coverage."""
    assert compute_gap_score([], [1, 2, 3]) == 0.0


def test_gap_score_partial():
    """50% coverage."""
    assert compute_gap_score([1, 2], [3, 4]) == 50.0


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
