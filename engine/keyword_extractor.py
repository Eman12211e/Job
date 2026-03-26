"""Core regex engine for extracting and counting skill keywords in job postings.

Uses word-boundary matching to prevent false positives (e.g., "FEA" in "features").
Each skill can have multiple aliases — if ANY alias matches a posting, it counts
as one mention of that canonical skill (no double-counting within a posting).
"""

import re
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List


def load_keywords(filepath: str | Path) -> List[Dict]:
    """Load keywords.json and return the list of skill dicts.

    Each dict has keys: canonical, aliases, category, industries.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["skills"]


def _build_single_pattern(alias: str) -> re.Pattern:
    """Build a regex pattern for one alias with proper word boundaries.

    For aliases that start/end with non-word characters (like GD&T or C++),
    standard \\b won't work correctly. We use lookarounds instead.
    """
    escaped = re.escape(alias)

    # Check if the first character is a word character (letter, digit, underscore)
    if alias[0].isalnum() or alias[0] == "_":
        prefix = r"\b"
    else:
        prefix = r"(?<!\w)"

    # Check if the last character is a word character
    if alias[-1].isalnum() or alias[-1] == "_":
        suffix = r"\b"
    else:
        suffix = r"(?!\w)"

    return re.compile(prefix + escaped + suffix, re.IGNORECASE)


def build_regex_patterns(skills: List[Dict]) -> Dict[str, List[re.Pattern]]:
    """Pre-compile regex patterns for every alias of every skill.

    Returns a dict mapping canonical skill name to a list of compiled
    regex patterns (one per alias), all case-insensitive.
    """
    patterns = {}
    for skill in skills:
        canonical = skill["canonical"]
        patterns[canonical] = [
            _build_single_pattern(alias) for alias in skill["aliases"]
        ]
    return patterns


def count_skill_mentions(
    postings_df: pd.DataFrame,
    patterns: Dict[str, List[re.Pattern]],
    text_columns: List[str] = None,
) -> pd.DataFrame:
    """Count how many job postings mention each skill at least once.

    For each posting, concatenates the text columns into one string.
    For each skill, checks if ANY alias pattern matches that string.
    A posting mentioning both "FEA" and "Finite Element Analysis"
    still counts as only ONE mention for that canonical skill.

    Returns a DataFrame with columns: [canonical, mention_count]
    """
    if text_columns is None:
        text_columns = ["description", "requirements"]

    # Build a single text column for searching
    combined_texts = postings_df[text_columns].fillna("").agg(" ".join, axis=1)

    results = []
    for canonical, pattern_list in patterns.items():
        count = 0
        for text in combined_texts:
            for pattern in pattern_list:
                if pattern.search(text):
                    count += 1
                    break  # One match per posting is enough
        results.append({"canonical": canonical, "mention_count": count})

    return pd.DataFrame(results)


def extract_skills_from_text(
    text: str,
    patterns: Dict[str, List[re.Pattern]],
) -> List[str]:
    """Given arbitrary text (e.g., a resume), return canonical skill names found.

    Used by gap_analysis.py to detect what skills a user already has.
    """
    found = []
    for canonical, pattern_list in patterns.items():
        for pattern in pattern_list:
            if pattern.search(text):
                found.append(canonical)
                break
    return found
