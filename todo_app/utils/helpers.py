"""Date / time / filename helpers used across the app."""
from __future__ import annotations

import datetime as _dt
import os
import re
from pathlib import Path
from typing import Optional


def now_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Return current local time as a formatted string."""
    return _dt.datetime.now().strftime(fmt)


def parse_date(value: str, fmt: str = "%Y-%m-%d") -> Optional[_dt.date]:
    """Parse a YYYY-MM-DD string into a date. Returns None on failure."""
    if not value:
        return None
    try:
        return _dt.datetime.strptime(value, fmt).date()
    except (ValueError, TypeError):
        return None


def parse_time(value: str, fmt: str = "%H:%M") -> Optional[_dt.time]:
    """Parse an HH:MM string into a time. Returns None on failure."""
    if not value:
        return None
    try:
        return _dt.datetime.strptime(value, fmt).time()
    except (ValueError, TypeError):
        return None


def format_date(value: Optional[_dt.date], fmt: str = "%Y-%m-%d") -> str:
    """Format a date as a string. Returns '' for None."""
    if value is None:
        return ""
    return value.strftime(fmt)


def format_time(value: Optional[_dt.time], fmt: str = "%H:%M") -> str:
    """Format a time as a string. Returns '' for None."""
    if value is None:
        return ""
    return value.strftime(fmt)


def combine_date_time(
    date_value: Optional[_dt.date], time_value: Optional[_dt.time]
) -> Optional[_dt.datetime]:
    """Combine a date and time into a datetime. Returns None if either is missing."""
    if date_value is None:
        return None
    if time_value is None:
        return _dt.datetime.combine(date_value, _dt.time(0, 0))
    return _dt.datetime.combine(date_value, time_value)


def humanize_duration(minutes: Optional[int]) -> str:
    """Convert a minute count into a human string: '1h 30m', '45m', etc."""
    if minutes is None or minutes <= 0:
        return ""
    hours, mins = divmod(int(minutes), 60)
    if hours and mins:
        return f"{hours}h {mins}m"
    if hours:
        return f"{hours}h"
    return f"{mins}m"


def safe_filename(name: str, fallback: str = "export") -> str:
    """Sanitize a string for use as a filename."""
    if not name:
        return fallback
    cleaned = re.sub(r"[^\w\-\.]+", "_", name.strip())
    return cleaned or fallback


def ensure_dir(path: str | os.PathLike[str]) -> Path:
    """Create the directory if missing and return the Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def is_overdue(
    due_date: Optional[_dt.date], due_time: Optional[_dt.time], status: str
) -> bool:
    """Return True when a task is past its due date/time and not yet completed/cancelled."""
    if status in ("Completed", "Cancelled") or due_date is None:
        return False
    due_dt = combine_date_time(due_date, due_time)
    if due_dt is None:
        return False
    return _dt.datetime.now() > due_dt


def days_between(start: _dt.date, end: _dt.date) -> int:
    """Return inclusive day count between two dates."""
    return max(0, (end - start).days)


def greeting_for_hour(hour: int) -> str:
    """Return a greeting for a given hour of the day (0-23)."""
    if 5 <= hour < 12:
        return "Good Morning"
    if 12 <= hour < 17:
        return "Good Afternoon"
    if 17 <= hour < 22:
        return "Good Evening"
    return "Good Night"


def start_of_day(d: _dt.date) -> _dt.datetime:
    return _dt.datetime.combine(d, _dt.time(0, 0))


def end_of_day(d: _dt.date) -> _dt.datetime:
    return _dt.datetime.combine(d, _dt.time(23, 59, 59))
