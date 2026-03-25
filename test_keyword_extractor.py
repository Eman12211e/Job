"""Tests for the regex keyword extraction engine.

Validates word-boundary matching, false-positive prevention,
and correct per-posting deduplication.
"""

import pandas as pd
import sys
from pathlib import Path

# Add project root to path so imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.keyword_extractor import (
    build_regex_patterns,
    count_skill_mentions,
    extract_skills_from_text,
    _build_single_pattern,
)


# ── Helper: build patterns from a simple list ─────────────────────────

def _make_skills(*entries):
    """Quick helper to build skill dicts for testing."""
    skills = []
    for canonical, aliases in entries:
        skills.append({
            "canonical": canonical,
            "aliases": aliases,
            "category": "test",
            "industries": [],
        })
    return skills


# ── Tests: False-positive prevention ──────────────────────────────────

def test_fea_does_not_match_features():
    """'FEA' pattern must NOT match inside the word 'features'."""
    skills = _make_skills(("FEA", ["FEA"]))
    patterns = build_regex_patterns(skills)
    text = "This role requires advanced features and analytical tools."
    result = extract_skills_from_text(text, patterns)
    assert "FEA" not in result, f"FEA incorrectly matched in: {text}"


def test_fea_does_not_match_safety():
    """'FEA' should not match in 'safety' or 'safe'."""
    skills = _make_skills(("FEA", ["FEA"]))
    patterns = build_regex_patterns(skills)
    text = "Must follow safety protocols and interface guidelines."
    result = extract_skills_from_text(text, patterns)
    assert "FEA" not in result


def test_fea_matches_standalone():
    """'FEA' pattern must match standalone 'FEA'."""
    skills = _make_skills(("FEA", ["FEA", "Finite Element Analysis"]))
    patterns = build_regex_patterns(skills)
    text = "Experience with FEA and structural analysis required."
    result = extract_skills_from_text(text, patterns)
    assert "FEA" in result


def test_fe_exam_does_not_match_features():
    """'FE exam' should not match when 'fe' is inside 'features'."""
    skills = _make_skills(("FE Exam", ["FE exam"]))
    patterns = build_regex_patterns(skills)
    text = "Key features of this role include interface design."
    result = extract_skills_from_text(text, patterns)
    assert "FE Exam" not in result


# ── Tests: Special characters ─────────────────────────────────────────

def test_gdt_with_ampersand():
    """GD&T must match despite the & character."""
    skills = _make_skills(("GD&T", ["GD&T"]))
    patterns = build_regex_patterns(skills)
    text = "Knowledge of GD&T per ASME Y14.5 is required."
    result = extract_skills_from_text(text, patterns)
    assert "GD&T" in result


def test_cpp_with_plus():
    """C++ must match correctly."""
    skills = _make_skills(("C++", ["C++", "C/C++"]))
    patterns = build_regex_patterns(skills)
    text = "Proficiency in C++ for embedded systems."
    result = extract_skills_from_text(text, patterns)
    assert "C++" in result


# ── Tests: Case insensitivity ─────────────────────────────────────────

def test_case_insensitive_solidworks():
    """'solidworks' should match 'SolidWorks' and 'SOLIDWORKS'."""
    skills = _make_skills(("SolidWorks", ["SolidWorks", "SOLIDWORKS"]))
    patterns = build_regex_patterns(skills)

    for text in ["Experience with solidworks", "Use SOLIDWORKS daily"]:
        result = extract_skills_from_text(text, patterns)
        assert "SolidWorks" in result, f"Failed to match in: {text}"


# ── Tests: No double-counting ─────────────────────────────────────────

def test_no_double_counting_per_posting():
    """A posting mentioning both 'FEA' and 'Finite Element Analysis'
    should count as only 1 mention."""
    skills = _make_skills(("FEA", ["FEA", "Finite Element Analysis"]))
    patterns = build_regex_patterns(skills)

    df = pd.DataFrame({
        "description": ["Must have FEA experience. Finite Element Analysis is key."],
        "requirements": ["FEA tools required."],
    })

    result = count_skill_mentions(df, patterns)
    fea_count = result[result["canonical"] == "FEA"]["mention_count"].values[0]
    assert fea_count == 1, f"Expected 1, got {fea_count}"


def test_multiple_postings_counted_separately():
    """Two postings each mentioning a skill should give count = 2."""
    skills = _make_skills(("Python", ["Python"]))
    patterns = build_regex_patterns(skills)

    df = pd.DataFrame({
        "description": ["Python required", "We use Python"],
        "requirements": ["", ""],
    })

    result = count_skill_mentions(df, patterns)
    count = result[result["canonical"] == "Python"]["mention_count"].values[0]
    assert count == 2


# ── Tests: Multi-word aliases ─────────────────────────────────────────

def test_multiword_alias_boundary():
    """'FE analysis' should match as a phrase, not partial."""
    skills = _make_skills(("FEA", ["FE analysis"]))
    patterns = build_regex_patterns(skills)

    text = "Conduct FE analysis of structural components."
    result = extract_skills_from_text(text, patterns)
    assert "FEA" in result

    # Should NOT match when words are separated by other content
    text2 = "safe analysis techniques"
    result2 = extract_skills_from_text(text2, patterns)
    assert "FEA" not in result2


# ── Tests: Zero mentions ──────────────────────────────────────────────

def test_skill_not_present_returns_zero():
    """A skill not mentioned in any posting should have count 0."""
    skills = _make_skills(("CATIA", ["CATIA"]))
    patterns = build_regex_patterns(skills)

    df = pd.DataFrame({
        "description": ["We use SolidWorks and AutoCAD."],
        "requirements": ["No CATIA needed."],
    })
    # Wait — "No CATIA needed" actually contains CATIA. Let me fix.
    df = pd.DataFrame({
        "description": ["We use SolidWorks and AutoCAD."],
        "requirements": ["3D modeling experience required."],
    })

    result = count_skill_mentions(df, patterns)
    count = result[result["canonical"] == "CATIA"]["mention_count"].values[0]
    assert count == 0


if __name__ == "__main__":
    # Simple test runner
    import traceback
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    passed = 0
    failed = 0
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
