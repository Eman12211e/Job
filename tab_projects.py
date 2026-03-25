"""Tab 4 — High-Impact Projects: cards with deliverables + resume bullets."""

import json
import streamlit as st
from pathlib import Path
from typing import List
from config.settings import DATA_DIR


def _load_projects() -> List[dict]:
    """Load projects from JSON."""
    path = DATA_DIR / "projects.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["projects"]


def render_projects_tab(industries: List[str]) -> None:
    """Display project cards filtered by selected industries."""
    st.header("High-Impact Projects")
    st.write(
        "Systems-integration projects that produce a GitHub portfolio "
        "and ready-to-use resume bullets. Filtered to your target industries."
    )

    projects = _load_projects()
    filtered = [p for p in projects if p["industry"] in industries]

    if not filtered:
        st.info("No projects found for the selected industries. "
                "Try adding more industries in the sidebar.")
        return

    # Difficulty filter
    difficulties = sorted(set(p["difficulty"] for p in filtered))
    selected_diff = st.multiselect(
        "Filter by difficulty",
        options=difficulties,
        default=difficulties,
    )
    filtered = [p for p in filtered if p["difficulty"] in selected_diff]

    for project in filtered:
        diff_badge = {
            "beginner": "Beginner",
            "intermediate": "Intermediate",
            "advanced": "Advanced",
        }.get(project["difficulty"], project["difficulty"])

        with st.expander(
            f"{project['title']}  |  {project['industry']}  |  {diff_badge}",
            expanded=False,
        ):
            st.markdown(f"**{project['description']}**")
            st.markdown(f"*Estimated time: {project['estimated_hours']} hours*")

            st.markdown("**Skills Demonstrated:**")
            st.write(", ".join(project["skills_demonstrated"]))

            st.markdown("**Deliverables:**")
            for d in project["deliverables"]:
                st.markdown(f"- {d}")

            st.markdown("**Copy-Paste Resume Bullets:**")
            all_bullets = []
            for bullet in project["resume_bullets"]:
                st.markdown(f"- {bullet}")
                all_bullets.append(bullet)

            # Copyable block
            st.code("\n".join(f"* {b}" for b in all_bullets), language=None)
