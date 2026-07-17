"""Application-wide constants and enumerations."""
from __future__ import annotations

from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# App identity
# ---------------------------------------------------------------------------
APP_NAME: str = "Akena Todo"
APP_VERSION: str = "2.0.0"
APP_AUTHOR: str = "Akena"

# ---------------------------------------------------------------------------
# Priorities
# ---------------------------------------------------------------------------
PRIORITIES: List[str] = ["Low", "Medium", "High", "Critical"]

PRIORITY_COLORS: Dict[str, str] = {
    "Low": "#3B82F6",        # blue
    "Medium": "#F59E0B",     # amber
    "High": "#EF4444",       # red
    "Critical": "#A855F7",   # purple
}

PRIORITY_ORDER: Dict[str, int] = {
    "Critical": 0,
    "High": 1,
    "Medium": 2,
    "Low": 3,
}

# ---------------------------------------------------------------------------
# Statuses
# ---------------------------------------------------------------------------
STATUSES: List[str] = [
    "Not Started",
    "In Progress",
    "Completed",
    "Cancelled",
    "Overdue",
]

STATUS_COLORS: Dict[str, str] = {
    "Not Started": "#94A3B8",   # slate
    "In Progress": "#0EA5E9",   # sky
    "Completed": "#22C55E",     # green
    "Cancelled": "#6B7280",     # gray
    "Overdue": "#DC2626",       # red
}

# ---------------------------------------------------------------------------
# Repeat / Reminders
# ---------------------------------------------------------------------------
REPEAT_OPTIONS: List[str] = ["None", "Daily", "Weekly", "Monthly", "Yearly"]

REMINDER_OPTIONS: List[Tuple[str, int]] = [
    ("None", 0),
    ("5 minutes before", 5),
    ("10 minutes before", 10),
    ("30 minutes before", 30),
    ("1 hour before", 60),
    ("1 day before", 1440),
]

# ---------------------------------------------------------------------------
# Color tags (for visual tagging of tasks)
# ---------------------------------------------------------------------------
COLOR_TAGS: List[str] = [
    "#0EA5E9", "#22C55E", "#F59E0B", "#EF4444",
    "#A855F7", "#EC4899", "#14B8A6", "#64748B",
]

# ---------------------------------------------------------------------------
# Default categories seeded on first launch
# ---------------------------------------------------------------------------
DEFAULT_CATEGORIES: List[str] = [
    "University",
    "Coding",
    "Cloud Computing",
    "DevOps",
    "AI",
    "Projects",
    "Football",
    "Exercise",
    "Reading",
    "Personal",
    "Shopping",
    "Health",
    "Meetings",
    "Others",
]

# ---------------------------------------------------------------------------
# Themes
# ---------------------------------------------------------------------------
THEMES: List[str] = ["Light", "Dark"]

# ---------------------------------------------------------------------------
# Pomodoro defaults (minutes)
# ---------------------------------------------------------------------------
POMODORO_WORK: int = 25
POMODORO_SHORT_BREAK: int = 5
POMODORO_LONG_BREAK: int = 15
POMODORO_CYCLES_BEFORE_LONG: int = 4

# ---------------------------------------------------------------------------
# File names
# ---------------------------------------------------------------------------
DB_FILENAME: str = "akena_todo.db"
SETTINGS_KEY: str = "app_settings"
LOG_FILENAME: str = "app.log"
