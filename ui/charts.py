"""Plotly chart builders — returns Figure objects, no Streamlit calls."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from config.settings import CATEGORY_COLORS


def keyword_frequency_bar(ranked_df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    """Horizontal bar chart of top N skills by priority score."""
    df = ranked_df.head(top_n).copy()
    # Reverse so highest is at top
    df = df.iloc[::-1]

    colors = [CATEGORY_COLORS.get(cat, "#6B7280") for cat in df["category"]]

    fig = go.Figure(
        go.Bar(
            x=df["priority_score"],
            y=df["canonical"],
            orientation="h",
            marker_color=colors,
            text=df["priority_score"].apply(lambda x: f"{x:.0f}%"),
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Priority Score: %{x:.1f}%<br>"
                "<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title="Top Skills by Priority Score",
        xaxis_title="Priority Score (% of postings mentioning this skill)",
        yaxis_title="",
        height=max(400, top_n * 32),
        margin=dict(l=10, r=80, t=50, b=40),
        xaxis=dict(range=[0, 105]),
    )
    return fig


def gap_donut(present_count: int, missing_count: int) -> go.Figure:
    """Donut chart showing skills coverage percentage."""
    total = present_count + missing_count
    pct = round(present_count / total * 100) if total > 0 else 0

    fig = go.Figure(
        go.Pie(
            values=[present_count, missing_count],
            labels=["Skills You Have", "Skills to Develop"],
            hole=0.6,
            marker_colors=["#059669", "#DC2626"],
            textinfo="label+value",
            hovertemplate="%{label}: %{value}<extra></extra>",
        )
    )
    fig.update_layout(
        annotations=[
            dict(text=f"{pct}%", x=0.5, y=0.5, font_size=36, showarrow=False)
        ],
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
    )
    return fig


def category_breakdown(ranked_df: pd.DataFrame, top_n: int = 20) -> go.Figure:
    """Pie chart showing skill distribution by category for the top N skills."""
    df = ranked_df.head(top_n)
    cat_counts = df["category"].value_counts().reset_index()
    cat_counts.columns = ["category", "count"]

    colors = [CATEGORY_COLORS.get(c, "#6B7280") for c in cat_counts["category"]]

    fig = go.Figure(
        go.Pie(
            values=cat_counts["count"],
            labels=cat_counts["category"],
            marker_colors=colors,
            textinfo="label+percent",
            hovertemplate="%{label}: %{value} skills<extra></extra>",
        )
    )
    fig.update_layout(
        title=f"Skill Category Distribution (Top {top_n})",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig
