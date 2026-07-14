"""Theme manager - centralized colour palette and CTk appearance.

The application supports Light and Dark modes. Switching themes at runtime
re-applies the configured palette to every active CustomTkinter window.
"""
from __future__ import annotations

import customtkinter as ctk
from typing import Dict


# ---------------------------------------------------------------------------
# Colour palettes
# ---------------------------------------------------------------------------
LIGHT_PALETTE: Dict[str, str] = {
    "bg": "#F4F6FA",
    "surface": "#FFFFFF",
    "surface_alt": "#F1F5F9",
    "sidebar": "#FFFFFF",
    "sidebar_active": "#E0F2FE",
    "topbar": "#FFFFFF",
    "text": "#0F172A",
    "text_muted": "#475569",
    "text_inverse": "#FFFFFF",
    "border": "#E2E8F0",
    "accent": "#0EA5E9",
    "accent_hover": "#0284C7",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "critical": "#A855F7",
    "shadow": "#0F172A",
    "card": "#FFFFFF",
    "input_bg": "#F8FAFC",
}

DARK_PALETTE: Dict[str, str] = {
    "bg": "#0B1220",
    "surface": "#111827",
    "surface_alt": "#1F2937",
    "sidebar": "#0F172A",
    "sidebar_active": "#1E293B",
    "topbar": "#0F172A",
    "text": "#F1F5F9",
    "text_muted": "#94A3B8",
    "text_inverse": "#0F172A",
    "border": "#1E293B",
    "accent": "#38BDF8",
    "accent_hover": "#0EA5E9",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "danger": "#F87171",
    "critical": "#C084FC",
    "shadow": "#000000",
    "card": "#111827",
    "input_bg": "#1F2937",
}


PALETTES = {"Light": LIGHT_PALETTE, "Dark": DARK_PALETTE}


class ThemeManager:
    """Applies the active theme to all CustomTkinter widgets."""

    def __init__(self) -> None:
        self._current: str = "Dark"
        self._palette: Dict[str, str] = dict(DARK_PALETTE)

    @property
    def name(self) -> str:
        return self._current

    @property
    def palette(self) -> Dict[str, str]:
        return self._palette

    def color(self, key: str) -> str:
        return self._palette.get(key, "#FFFFFF")

    def apply(self, theme: str) -> None:
        """Switch the global CustomTkinter theme and update the palette."""
        theme = theme if theme in PALETTES else "Dark"
        self._current = theme
        self._palette = dict(PALETTES[theme])
        ctk.set_appearance_mode("Light" if theme == "Light" else "Dark")
        ctk.set_default_color_theme("blue")


# Module-level singleton
THEME = ThemeManager()
