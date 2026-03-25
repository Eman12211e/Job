"""Dynamic Career Roadmap Tool — Main Streamlit App.

Helps mechanical engineering students and recent grads build
ATS-optimized resumes based on real job posting keyword analysis.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from config.settings import (
    APP_TITLE, APP_ICON, DATA_DIR, JOB_POSTINGS_DIR,
    INDUSTRY_FILE_MAP, DEFAULT_TOP_N, LAST_UPDATED,
)
from engine.keyword_extractor import load_keywords, build_regex_patterns, count_skill_mentions
from engine.ranking import compute_priority_scores
from ui.sidebar import render_sidebar
from ui.tab_ranking import render_ranking_tab
from ui.tab_resume import render_resume_tab
from ui.tab_gap import render_gap_tab
from ui.tab_projects import render_projects_tab
from ui.tab_learning import render_learning_tab
from export.pdf_export import generate_pdf


# ── Page config ────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title(f"{APP_ICON} {APP_TITLE}")
st.caption(f"Data-driven skill rankings from real job postings | Last updated: {LAST_UPDATED}")


# ── Cached data loaders ───────────────────────────────────────────────

@st.cache_data
def load_postings(industries: tuple) -> pd.DataFrame:
    """Load and concatenate job posting CSVs for selected industries."""
    frames = []
    for industry in industries:
        filename = INDUSTRY_FILE_MAP.get(industry)
        if filename:
            filepath = JOB_POSTINGS_DIR / filename
            if filepath.exists():
                df = pd.read_csv(filepath)
                frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


@st.cache_data
def load_skills_data():
    """Load keywords.json and return the skills list."""
    return load_keywords(DATA_DIR / "keywords.json")


@st.cache_data
def get_patterns(_skills_data, _cache_key=None):
    """Build compiled regex patterns (cached)."""
    return build_regex_patterns(_skills_data)



@st.cache_data
def run_analysis(postings_hash: str, _postings_df, _patterns, _skills_data):
    """Run keyword extraction and ranking (cached on postings hash)."""
    mention_df = count_skill_mentions(_postings_df, _patterns)
    total = len(_postings_df)
    ranked_df = compute_priority_scores(mention_df, total, _skills_data)
    return ranked_df


# ── Sidebar ────────────────────────────────────────────────────────────
user_config = render_sidebar()

if not user_config["industries"]:
    st.warning("Please select at least one industry in the sidebar to begin.")
    st.stop()


# ── Load & analyze ────────────────────────────────────────────────────
industries_key = tuple(sorted(user_config["industries"]))
postings_df = load_postings(industries_key)

if postings_df.empty:
    st.error("No job posting data found. Check the data/job_postings/ folder.")
    st.stop()

skills_data = load_skills_data()
patterns = get_patterns(skills_data, _cache_key="patterns")

# Create a hash key for caching the analysis
postings_hash = str(hash(tuple(postings_df["job_id"].tolist())))
ranked_df = run_analysis(postings_hash, postings_df, patterns, skills_data)

# Show summary metrics
total_postings = len(postings_df)
total_skills = len(ranked_df[ranked_df["mention_count"] > 0])
top_skill = ranked_df.iloc[0]["canonical"] if len(ranked_df) > 0 else "N/A"

col1, col2, col3 = st.columns(3)
col1.metric("Job Postings Analyzed", total_postings)
col2.metric("Skills Tracked", total_skills)
col3.metric("Top Skill", top_skill)

st.markdown("---")

# ── Tabs ───────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Keyword Rankings",
    "Resume Bullets",
    "Skills Gap",
    "Projects",
    "Learning Paths",
])

top_n = user_config["top_n"]

with tab1:
    render_ranking_tab(ranked_df, top_n=top_n)

with tab2:
    render_resume_tab(ranked_df, user_config, skills_data)

with tab3:
    render_gap_tab(ranked_df, patterns, top_n=top_n)

with tab4:
    render_projects_tab(user_config["industries"])

with tab5:
    render_learning_tab(ranked_df)


# ── PDF Export ─────────────────────────────────────────────────────────
if user_config["export_pdf"]:
    gap_results = st.session_state.get("gap_results")
    bullets = st.session_state.get("generated_bullets")

    pdf_bytes = generate_pdf(
        user_config=user_config,
        ranked_skills=ranked_df.head(25).to_dict("records"),
        gap_results=gap_results,
        bullets=bullets,
    )
    st.sidebar.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name="career_roadmap_report.pdf",
        mime="application/pdf",
    )
