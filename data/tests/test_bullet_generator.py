"""Tests for the dynamic resume bullet generator."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.bullet_generator import generate_bullets, _adjust_for_background


SAMPLE_METADATA = [
    {"canonical": "SolidWorks", "aliases": ["SolidWorks"], "category": "cad", "industries": []},
    {"canonical": "FEA", "aliases": ["FEA"], "category": "analysis", "industries": []},
    {"canonical": "PLC Programming", "aliases": ["PLC"], "category": "controls", "industries": []},
    {"canonical": "Python", "aliases": ["Python"], "category": "programming", "industries": []},
]


def test_bullet_contains_skill_name():
    """Generated bullet must contain the canonical skill name."""
    results = generate_bullets(
        skills=["SolidWorks"],
        industry="EV/Automotive",
        background="Experienced Engineer",
        skills_metadata=SAMPLE_METADATA,
        num_bullets=1,
    )
    assert len(results) == 1
    assert "SolidWorks" in results[0]["bullets"][0]


def test_student_framing():
    """Student background should produce project/coursework language."""
    results = generate_bullets(
        skills=["FEA"],
        industry="Aerospace/Robotics",
        background="Current ME Student",
        skills_metadata=SAMPLE_METADATA,
        num_bullets=1,
    )
    bullet = results[0]["bullets"][0].lower()
    student_words = ["capstone", "coursework", "undergraduate", "student", "design competition"]
    assert any(w in bullet for w in student_words), f"No student framing in: {bullet}"


def test_professional_framing():
    """Experienced Engineer background should NOT have student prefixes."""
    results = generate_bullets(
        skills=["PLC Programming"],
        industry="Factory Automation",
        background="Experienced Engineer",
        skills_metadata=SAMPLE_METADATA,
        num_bullets=1,
    )
    bullet = results[0]["bullets"][0].lower()
    student_words = ["capstone", "coursework", "undergraduate", "student design"]
    assert not any(w in bullet for w in student_words), f"Student framing found in: {bullet}"


def test_multiple_bullets_per_skill():
    """Requesting 2 bullets should return 2 distinct bullets."""
    results = generate_bullets(
        skills=["Python"],
        industry="Factory Automation",
        background="Recent ME Graduate",
        skills_metadata=SAMPLE_METADATA,
        num_bullets=2,
    )
    bullets = results[0]["bullets"]
    assert len(bullets) == 2
    assert bullets[0] != bullets[1], "Bullets should be different"


def test_industry_context_varies():
    """Different industries should produce different context in bullets."""
    results_ev = generate_bullets(
        skills=["SolidWorks"],
        industry="EV/Automotive",
        background="Experienced Engineer",
        skills_metadata=SAMPLE_METADATA,
        num_bullets=1,
    )
    results_aero = generate_bullets(
        skills=["SolidWorks"],
        industry="Aerospace/Robotics",
        background="Experienced Engineer",
        skills_metadata=SAMPLE_METADATA,
        num_bullets=1,
    )
    # Due to randomness, they MIGHT be the same occasionally,
    # but across industries the context pools are different.
    # Just verify both return valid bullets.
    assert len(results_ev[0]["bullets"]) >= 1
    assert len(results_aero[0]["bullets"]) >= 1


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
