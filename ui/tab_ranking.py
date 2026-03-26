"""Tab 1 — Keyword Rankings: table + bar chart + category breakdown."""

import streamlit as st
import pandas as pd
from ui.charts import keyword_frequency_bar, category_breakdown
from config.settings import CHART_TOP_N


def render_ranking_tab(ranked_df: pd.DataFrame, top_n: int = 20) -> None:
    """Display the ranked skills table and Plotly charts."""
    st.header("Keyword Rankings")
    st.write(
        "Skills ranked by how frequently they appear in real job postings "
        "for your selected industries."
    )

    # Top bar chart
    chart_n = min(CHART_TOP_N, top_n)
    fig = keyword_frequency_bar(ranked_df, top_n=chart_n)
    st.plotly_chart(fig, use_container_width=True)

    # Category breakdown + data table side by side
    col1, col2 = st.columns([1, 2])

    with col1:
        cat_fig = category_breakdown(ranked_df, top_n=top_n)
        st.plotly_chart(cat_fig, use_container_width=True)

    with col2:
        st.subheader(f"Top {top_n} Skills — Full Table")
        display_df = ranked_df.head(top_n).copy()
        display_df.columns = ["Rank", "Skill", "Category", "Mentions", "Score (%)"]
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=min(700, top_n * 38 + 40),
        )

    # Expandable: show ALL skills
    with st.expander("Show all tracked skills"):
        full_df = ranked_df.copy()
        full_df.columns = ["Rank", "Skill", "Category", "Mentions", "Score (%)"]
        st.dataframe(full_df, use_container_width=True, hide_index=True)
