"""App-wide constants and configuration."""

from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
JOB_POSTINGS_DIR = DATA_DIR / "job_postings"

# ── App metadata ───────────────────────────────────────────────────────
APP_TITLE = "Engineering Career Roadmap"
APP_ICON = "🎯"
LAST_UPDATED = "March 2026"

# ── Industry options ───────────────────────────────────────────────────
INDUSTRIES = ["EV/Automotive", "Factory Automation", "Aerospace/Robotics"]

INDUSTRY_FILE_MAP = {
    "EV/Automotive": "ev_automotive.csv",
    "Factory Automation": "factory_automation.csv",
    "Aerospace/Robotics": "aerospace_robotics.csv",
}

# ── Background options ─────────────────────────────────────────────────
BACKGROUNDS = [
    "Current ME Student",
    "Recent ME Graduate",
    "Career Changer",
    "Experienced Engineer",
]

# ── Chart colours (one per category) ──────────────────────────────────
CATEGORY_COLORS = {
    "cad": "#1B73E8",
    "analysis": "#E8710A",
    "controls": "#0D9488",
    "manufacturing": "#7C3AED",
    "standards": "#DC2626",
    "quality": "#CA8A04",
    "programming": "#2563EB",
    "certifications": "#059669",
    "soft_skills": "#6B7280",
}

# ── Defaults ───────────────────────────────────────────────────────────
DEFAULT_TOP_N = 20
CHART_TOP_N = 15
