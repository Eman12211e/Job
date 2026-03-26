"""Tab 2 — ATS Resume Kit: pick skills, generate copy-paste bullets."""

import streamlit as st
import pandas as pd
from typing import List, Dict
from engine.bullet_generator import generate_bullets


def render_resume_tab(
    ranked_df: pd.DataFrame,
    user_config: Dict,
    skills_metadata: List[Dict],
) -> None:
    """Let user pick skills from the ranked list and generate resume bullets."""
    st.header("ATS Resume Bullet Generator")
    st.write(
        "Select skills below to generate ready-to-use resume bullets "
        "packed with the exact keywords recruiters search for."
    )

    # Skill selector — default to top 5
    top_skills = ranked_df.head(10)["canonical"].tolist()
    selected = st.multiselect(
        "Pick skills to generate bullets for",
        options=ranked_df["canonical"].tolist(),
        default=top_skills[:5],
        help="Each skill generates 2 ATS-optimized bullet points.",
    )

    if not selected:
        st.info("Select at least one skill above to generate bullets.")
        return

    # Industry for context — use the first selected industry
    industry = user_config["industries"][0] if user_config["industries"] else "EV/Automotive"
    background = user_config["background"]

    # Generate
    results = generate_bullets(
        skills=selected,
        industry=industry,
        background=background,
        skills_metadata=skills_metadata,
        num_bullets=2,
    )

    # Display
    all_bullets = []
    for entry in results:
        score = ranked_df.loc[
            ranked_df["canonical"] == entry["skill"], "priority_score"
        ]
        score_val = score.values[0] if len(score) > 0 else 0

        st.subheader(f"{entry['skill']}  — Score: {score_val:.0f}%")
        for bullet in entry["bullets"]:
            st.markdown(f"- {bullet}")
            all_bullets.append(bullet)
        st.markdown("---")

    # Copy-all section
    if all_bullets:
        st.subheader("Copy All Bullets")
        combined = "\n".join(f"• {b}" for b in all_bullets)
        st.code(combined, language=None)

    # Store in session state for PDF export
    st.session_state["generated_bullets"] = all_bullets
