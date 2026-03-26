"""Sidebar component — handles all user input selections."""

import streamlit as st
from typing import Dict
from config.settings import INDUSTRIES, BACKGROUNDS


def render_sidebar() -> Dict:
    """Render the sidebar and return user selections.

    Returns dict with keys: background, industries, export_pdf
    """
    st.sidebar.title("Career Roadmap")
    st.sidebar.caption("Data updated March 2026")

    background = st.sidebar.selectbox(
        "Your Background",
        options=BACKGROUNDS,
        index=0,
        help="Adjusts resume bullet language and project difficulty.",
    )

    industries = st.sidebar.multiselect(
        "Target Industries",
        options=INDUSTRIES,
        default=["EV/Automotive"],
        help="Select 1-3 industries to analyze job postings.",
    )

    st.sidebar.markdown("---")

    top_n = st.sidebar.slider(
        "Top skills to show",
        min_value=5,
        max_value=40,
        value=20,
        step=5,
    )

    st.sidebar.markdown("---")
    export_pdf = st.sidebar.button("Export Report to PDF", use_container_width=True)

    return {
        "background": background,
        "industries": industries,
        "top_n": top_n,
        "export_pdf": export_pdf,
    }
