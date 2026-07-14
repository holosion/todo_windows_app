"""Asset helper - generate small emoji-based icons used across the UI.

The app ships without bundled icon files; emoji are used as portable
"icons" that work in any environment (including Windows 11).
"""
from __future__ import annotations

from typing import Dict


# Sidebar / top-level navigation icons
NAV_ICONS: Dict[str, str] = {
    "dashboard": "\U0001F4CA",   # 📊
    "tasks": "\u2705",           # ✅
    "planner": "\u23F0",         # ⏰
    "calendar": "\U0001F4C5",    # 📅
    "stats": "\U0001F4C8",       # 📈
    "pomodoro": "\U0001F345",    # 🍅
    "settings": "\u2699\uFE0F",  # ⚙️
    "search": "\U0001F50D",      # 🔍
    "add": "\u2795",             # ➕
    "edit": "\u270F\uFE0F",      # ✏️
    "delete": "\U0001F5D1\uFE0F",  # 🗑️
    "save": "\U0001F4BE",        # 💾
    "back": "\u2190",            # ←
    "filter": "\U0001F39B\uFE0F",  # 🎛️
    "sort": "\U0001F500",        # 🔀
    "theme": "\U0001F319",       # 🌙
    "sun": "\u2600\uFE0F",       # ☀️
    "star": "\u2B50",            # ⭐
    "pin": "\U0001F4CC",         # 📌
    "archive": "\U0001F4E6",     # 📦
    "restore": "\u21A9\uFE0F",   # ↩️
    "duplicate": "\u2398",       # ⎘
    "play": "\u25B6\uFE0F",      # ▶️
    "pause": "\u23F8\uFE0F",     # ⏸️
    "stop": "\u23F9\uFE0F",      # ⏹️
    "reset": "\u27F3",           # ⟳
    "reminder": "\U0001F514",    # 🔔
    "bell_off": "\U0001F515",    # 🔕
    "notes": "\U0001F4DD",       # 📝
    "attachment": "\U0001F4CE",  # 📎
    "quotes": "\U0001F4AC",      # 💬
    "fire": "\U0001F525",        # 🔥
    "trophy": "\U0001F3C6",      # 🏆
}


def icon(name: str) -> str:
    """Return the emoji glyph for ``name``, falling back to a bullet."""
    return NAV_ICONS.get(name, "\u2022")
