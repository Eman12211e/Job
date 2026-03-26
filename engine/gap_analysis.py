"""Skills gap analysis — compares a user's resume against top-ranked skills."""

import pandas as pd
from typing import Dict, List, Tuple

from engine.keyword_extractor import extract_skills_from_text


def analyze_gap(
    resume_text: str,
    ranked_df: pd.DataFrame,
    patterns: Dict[str, list],
    top_n: int = 20,
) -> Tuple[List[Dict], List[Dict]]:
    """Compare user's resume skills against the top ranked skills.

    1. Extracts skills found in resume_text using regex patterns
    2. Takes the top_n skills from ranked_df
    3. Splits into skills the user has vs. skills they're missing

    Returns:
        (skills_present, skills_missing) — each a list of dicts with
        keys: canonical, priority_score, rank
    """
    user_skills = set(extract_skills_from_text(resume_text, patterns))
    top_skills = ranked_df.head(top_n)

    skills_present = []
    skills_missing = []

    for _, row in top_skills.iterrows():
        entry = {
            "canonical": row["canonical"],
            "priority_score": row["priority_score"],
            "rank": row["rank"],
            "category": row["category"],
        }
        if row["canonical"] in user_skills:
            skills_present.append(entry)
        else:
            skills_missing.append(entry)

    return skills_present, skills_missing


def compute_gap_score(
    skills_present: List[Dict],
    skills_missing: List[Dict],
) -> float:
    """Return a percentage: how many of the top skills the user has.

    100% means the user has all top skills. 0% means none.
    """
    total = len(skills_present) + len(skills_missing)
    if total == 0:
        return 0.0
    return round(len(skills_present) / total * 100, 1)
