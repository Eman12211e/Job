"""Tab: Career Audit — The 'Two-Step' MVP Logic Flow.

Step 1 (Discovery): Show the user what their target industry demands.
Step 2 (Audit): Paste resume, get a match score, missing skills checklist,
                and a direct action plan to close the gap.

This is the PROACTIVE approach — not "why you failed" but
"here's exactly what to build by next month."
"""

import json
import streamlit as st
import pandas as pd
from typing import Dict, List

from engine.keyword_extractor import extract_skills_from_text
from config.settings import DATA_DIR


# ── Helpers ────────────────────────────────────────────────────────────

def _load_learning_paths() -> Dict[str, dict]:
    """Return a skill -> course mapping."""
    path = DATA_DIR / "learning_paths.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {p["skill"]: p for p in data["learning_paths"]}


def _load_projects() -> List[dict]:
    path = DATA_DIR / "projects.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["projects"]


def _check_resume_gaps(
    resume_text: str,
    ranked_df: pd.DataFrame,
    patterns: dict,
    top_n: int = 15,
) -> dict:
    """Run the gap check and return structured results.

    Returns dict with: match_score, found_skills, missing_skills,
    top_missing (the highest-priority missing skill).
    """
    user_skills = set(extract_skills_from_text(resume_text, patterns))
    top_skills = ranked_df.head(top_n)

    found = []
    missing = []

    for _, row in top_skills.iterrows():
        entry = {
            "skill": row["canonical"],
            "score": row["priority_score"],
            "mentions": int(row["mention_count"]),
            "category": row["category"],
            "rank": int(row["rank"]),
        }
        if row["canonical"] in user_skills:
            found.append(entry)
        else:
            missing.append(entry)

    total = len(found) + len(missing)
    match_score = round(len(found) / total * 100, 1) if total > 0 else 0.0

    return {
        "match_score": match_score,
        "found": found,
        "missing": missing,
        "top_missing": missing[0] if missing else None,
        "total_checked": total,
    }


# ── Main render function ──────────────────────────────────────────────

def render_audit_tab(
    ranked_df: pd.DataFrame,
    patterns: dict,
    user_config: dict,
) -> None:
    """Render the Two-Step Career Audit tab."""

    industries = user_config["industries"]
    industry_label = ", ".join(industries)

    # ================================================================
    # STEP 1: THE DISCOVERY
    # ================================================================
    st.header("Step 1: Industry Discovery")
    st.caption("What do employers actually search for in 2026?")

    # Pull top 3 skills for the insight banner
    top3 = ranked_df.head(3)
    total_postings = ranked_df["mention_count"].max()  # approximate denominator

    # Insight banner
    st.info(
        f"**In 2026, {int(top3.iloc[0]['priority_score'])}% of "
        f"{industry_label} jobs require "
        f"'{top3.iloc[0]['canonical']}' and "
        f"'{top3.iloc[1]['canonical']}'.**  "
        f"'{top3.iloc[2]['canonical']}' follows at "
        f"{int(top3.iloc[2]['priority_score'])}%."
    )

    # Top skills as metric cards
    cols = st.columns(min(5, len(ranked_df)))
    for i, (_, row) in enumerate(ranked_df.head(5).iterrows()):
        with cols[i]:
            st.metric(
                label=row["canonical"],
                value=f"{row['priority_score']:.0f}%",
                help=f"Found in {int(row['mention_count'])} of the analyzed job postings",
            )

    # Quick demand chart (top 10 as horizontal bars using streamlit native)
    st.markdown("---")
    st.subheader("Industry Demand at a Glance")
    chart_df = ranked_df.head(10)[["canonical", "priority_score"]].copy()
    chart_df = chart_df.set_index("canonical")
    chart_df.columns = ["% of postings"]
    st.bar_chart(chart_df, horizontal=True)

    # ================================================================
    # STEP 2: THE AUDIT
    # ================================================================
    st.markdown("---")
    st.header("Step 2: Resume Audit")
    st.caption(
        "Paste your resume below to see your match score against "
        "the industry's top keywords."
    )

    resume_text = st.text_area(
        "Paste your resume text here:",
        height=200,
        placeholder=(
            "Copy and paste the text from your resume... "
            "The tool will scan for industry keywords and show your gaps."
        ),
        key="audit_resume_input",
    )

    uploaded = st.file_uploader(
        "Or upload a .txt file",
        type=["txt"],
        key="audit_file_upload",
    )
    if uploaded is not None:
        resume_text = uploaded.read().decode("utf-8")

    # Number of skills to check
    check_n = st.slider(
        "Number of top skills to audit against",
        min_value=5,
        max_value=30,
        value=15,
        step=5,
        key="audit_top_n",
    )

    if not resume_text:
        st.warning(
            "Paste your resume text above to start the audit. "
            "The more text you include, the more accurate the results."
        )
        return

    if not st.button("Run Career Audit", type="primary", key="audit_run_btn"):
        # Show cached results if they exist
        if "audit_results" not in st.session_state:
            return

    # Run the gap check
    results = _check_resume_gaps(resume_text, ranked_df, patterns, top_n=check_n)
    st.session_state["audit_results"] = results
    # Also store in gap_results for cross-tab use (Learning Paths tab reads this)
    st.session_state["gap_results"] = {
        "present": [{"canonical": s["skill"], "priority_score": s["score"], "rank": s["rank"], "category": s["category"]} for s in results["found"]],
        "missing": [{"canonical": s["skill"], "priority_score": s["score"], "rank": s["rank"], "category": s["category"]} for s in results["missing"]],
        "score": results["match_score"],
    }

    _render_results(results, industry_label, user_config)


def _render_results(results: dict, industry_label: str, user_config: dict) -> None:
    """Render the audit results with visual flair."""

    match_score = results["match_score"]
    found = results["found"]
    missing = results["missing"]
    top_missing = results["top_missing"]

    # ── Match Score Banner ────────────────────────────────────────
    st.markdown("---")
    st.subheader("Your Audit Results")

    col_score, col_delta, col_top = st.columns(3)

    with col_score:
        st.metric(
            label="Match Score",
            value=f"{match_score:.0f}%",
        )

    with col_delta:
        # How much they could gain by adding 3 skills
        potential_gain = min(len(missing), 3) / results["total_checked"] * 100
        st.metric(
            label="Potential Gain",
            value=f"+{potential_gain:.0f}%",
            delta=f"by adding {min(len(missing), 3)} skills",
            delta_color="normal",
        )

    with col_top:
        if top_missing:
            st.metric(
                label="Top Missing Keyword",
                value=top_missing["skill"],
                delta=f"In {top_missing['mentions']} postings",
                delta_color="off",
            )

    # ── Progress Bar ──────────────────────────────────────────────
    st.progress(match_score / 100, text=f"Industry Match: {match_score:.0f}%")

    # Color-coded message
    if match_score >= 80:
        st.success(
            "Your resume is highly competitive for this industry. "
            "Focus on fine-tuning keyword placement and quantifying achievements."
        )
    elif match_score >= 50:
        st.warning(
            "You have a solid foundation but are missing key skills that "
            "appear in the majority of postings. See the action plan below."
        )
    else:
        st.error(
            "Significant gaps detected. The action plan below prioritizes "
            "the highest-impact skills to add first."
        )

    # ── Skills Checklist ──────────────────────────────────────────
    st.markdown("---")

    col_have, col_need = st.columns(2)

    with col_have:
        st.subheader(f"Skills You Have ({len(found)})")
        for s in found:
            st.checkbox(
                f"**{s['skill']}** ({s['score']:.0f}%)",
                value=True,
                disabled=True,
                key=f"audit_found_{s['skill']}",
            )

    with col_need:
        st.subheader(f"Missing Skills ({len(missing)})")
        for s in missing:
            st.checkbox(
                f"**{s['skill']}** ({s['score']:.0f}%) - in {s['mentions']} postings",
                value=False,
                disabled=True,
                key=f"audit_missing_{s['skill']}",
            )

    # ── Action Plan ───────────────────────────────────────────────
    if not missing:
        return

    st.markdown("---")
    st.header("Your Action Plan")
    st.caption(
        "Unlike reactive tools that tell you why you failed, "
        "this plan tells you exactly what to build by next month."
    )

    course_map = _load_learning_paths()
    projects = _load_projects()
    selected_industries = user_config.get("industries", [])

    for i, skill_entry in enumerate(missing[:5], 1):
        skill = skill_entry["skill"]
        score = skill_entry["score"]

        with st.expander(
            f"Action {i}: Add **{skill}** to your profile ({score:.0f}% of postings)",
            expanded=(i <= 3),
        ):
            act_col1, act_col2 = st.columns(2)

            with act_col1:
                # Course recommendation
                st.markdown("**Learn It:**")
                if skill in course_map:
                    course = course_map[skill]
                    st.markdown(
                        f"[{course['codecademy_course']}]({course['url']}) "
                        f"({course['estimated_hours']} hours)"
                    )
                    st.caption(course["relevance"])
                else:
                    st.markdown(
                        "No Codecademy course mapped. "
                        "Consider vendor certification or YouTube tutorials."
                    )

            with act_col2:
                # Project recommendation
                st.markdown("**Prove It:**")
                matched_projects = [
                    p for p in projects
                    if skill in p.get("skills_demonstrated", [])
                    and p["industry"] in selected_industries
                ]
                if not matched_projects:
                    # Fallback: any project with this skill
                    matched_projects = [
                        p for p in projects
                        if skill in p.get("skills_demonstrated", [])
                    ]

                if matched_projects:
                    proj = matched_projects[0]
                    st.markdown(f"**{proj['title']}** ({proj['difficulty']})")
                    st.caption(f"{proj['estimated_hours']} hours")
                    if proj.get("resume_bullets"):
                        st.markdown("*Sample bullet:*")
                        st.code(proj["resume_bullets"][0], language=None)
                else:
                    st.markdown(
                        "Build a portfolio project demonstrating this skill "
                        "with quantified results."
                    )

    # ── Summary Box ───────────────────────────────────────────────
    st.markdown("---")
    total_hours = sum(
        course_map.get(s["skill"], {}).get("estimated_hours", 0)
        for s in missing[:5]
    )
    st.info(
        f"**Summary:** Adding the top {min(len(missing), 5)} missing skills "
        f"could raise your match score from **{match_score:.0f}%** to "
        f"**{min(100, match_score + len(missing[:5]) / results['total_checked'] * 100):.0f}%**. "
        f"Estimated study time: **{total_hours} hours** on Codecademy."
    )
