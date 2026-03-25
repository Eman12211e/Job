"""Tab 5 — Codecademy Learning Paths: maps gap skills to courses."""

import json
import streamlit as st
import pandas as pd
from pathlib import Path
from typing import List
from config.settings import DATA_DIR


def _load_learning_paths() -> dict:
    """Load learning paths JSON."""
    path = DATA_DIR / "learning_paths.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def render_learning_tab(ranked_df: pd.DataFrame) -> None:
    """Show Codecademy course recommendations mapped to top skills."""
    st.header("Codecademy Action Plan")
    st.write(
        "Courses mapped to the skills that matter most in your target industries. "
        "Prioritized by keyword ranking so you study what moves the needle first."
    )

    data = _load_learning_paths()
    paths = data["learning_paths"]
    unmapped_note = data.get("unmapped_note", "No course mapped.")

    # Build skill-to-course lookup
    course_map = {p["skill"]: p for p in paths}

    # Use gap results if available, otherwise use top ranked skills
    gap = st.session_state.get("gap_results")
    if gap and gap["missing"]:
        st.info("Showing courses for skills identified in your Gap Analysis.")
        target_skills = [s["canonical"] for s in gap["missing"]]
    else:
        st.info(
            "Run the Skills Gap Analysis first for personalized recommendations. "
            "Showing courses for top-ranked skills instead."
        )
        target_skills = ranked_df["canonical"].tolist()

    # Build recommendation table
    rows = []
    seen_courses = set()
    for skill in target_skills:
        if skill in course_map:
            p = course_map[skill]
            course_key = p["codecademy_course"]
            if course_key not in seen_courses:
                rows.append({
                    "Priority Skill": skill,
                    "Course": p["codecademy_course"],
                    "Hours": p["estimated_hours"],
                    "Why It Matters": p["relevance"],
                    "Link": p["url"],
                })
                seen_courses.add(course_key)

    if rows:
        st.subheader("Recommended Courses")
        for row in rows:
            col1, col2, col3 = st.columns([3, 1, 4])
            with col1:
                st.markdown(f"**{row['Course']}**")
                st.caption(f"For: {row['Priority Skill']}")
            with col2:
                st.metric("Hours", row["Hours"])
            with col3:
                st.write(row["Why It Matters"])
                st.markdown(f"[Open on Codecademy]({row['Link']})")
            st.markdown("---")

        # Total study time
        total_hours = sum(r["Hours"] for r in rows)
        st.metric("Total Estimated Study Time", f"{total_hours} hours")

    # Show unmapped skills
    unmapped = [s for s in target_skills if s not in course_map]
    if unmapped:
        st.subheader("Skills Without Codecademy Courses")
        st.write(unmapped_note)
        for skill in unmapped[:10]:
            st.markdown(f"- **{skill}** — consider vendor certification or YouTube tutorials")

    # Bonus recommendation
    st.markdown("---")
    st.subheader("Bonus: Emerging 2026 Skills")
    st.markdown(
        "- **AI for Mechanical Engineers** — If available on Codecademy, "
        "this combines ML with engineering data analysis.\n"
        "- **Data Visualization** — Plotly/Dash skills are increasingly "
        "requested for engineering dashboard roles."
    )
