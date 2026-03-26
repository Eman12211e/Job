"""Ranking engine that computes Priority Scores and sorts skills.

Priority Score = (mention_count / total_postings) * 100
A score of 80 means the skill appears in 80% of scanned job postings.
"""

import pandas as pd
from typing import List, Dict


def compute_priority_scores(
    mention_df: pd.DataFrame,
    total_postings: int,
    skills_metadata: List[Dict] = None,
) -> pd.DataFrame:
    """Compute Priority Score for each skill and sort descending.

    Parameters:
        mention_df: DataFrame with columns [canonical, mention_count]
        total_postings: total number of job postings scanned
        skills_metadata: optional list of skill dicts (from keywords.json)
                         used to attach the category column

    Returns:
        DataFrame with columns [rank, canonical, category, mention_count,
        priority_score] sorted descending by priority_score.
    """
    df = mention_df.copy()
    df["priority_score"] = (df["mention_count"] / total_postings * 100).round(1)

    # Attach category if metadata provided
    if skills_metadata:
        cat_map = {s["canonical"]: s["category"] for s in skills_metadata}
        df["category"] = df["canonical"].map(cat_map).fillna("other")
    else:
        df["category"] = "other"

    df = df.sort_values("priority_score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df[["rank", "canonical", "category", "mention_count", "priority_score"]]


def get_top_skills(ranked_df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Return the top N skills by priority score."""
    return ranked_df.head(n).copy()


def filter_by_category(
    ranked_df: pd.DataFrame, categories: List[str]
) -> pd.DataFrame:
    """Filter ranked skills to specific categories."""
    return ranked_df[ranked_df["category"].isin(categories)].copy()


def filter_by_industry(
    skills_metadata: List[Dict], industry: str
) -> List[Dict]:
    """Return only skills that are relevant to the given industry."""
    return [s for s in skills_metadata if industry in s.get("industries", [])]
