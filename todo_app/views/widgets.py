"""Reusable, themed CustomTkinter widgets used across multiple views."""
from __future__ import annotations

import datetime as _dt
from typing import Callable, Optional

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

from .theme import THEME


# ---------------------------------------------------------------------------
# Card
# ---------------------------------------------------------------------------
class Card(ctk.CTkFrame):
    """A rounded 'card' frame used everywhere in the UI."""

    def __init__(
        self,
        master,
        fg_color: Optional[str] = None,
        border_width: int = 0,
        corner_radius: int = 16,
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            fg_color=fg_color or THEME.color("card"),
            corner_radius=corner_radius,
            border_width=border_width,
            border_color=THEME.color("border"),
            **kwargs,
        )


# ---------------------------------------------------------------------------
# Stat tile
# ---------------------------------------------------------------------------
class StatTile(Card):
    """A small tile that shows a label, value, and an accent icon."""

    def __init__(
        self,
        master,
        title: str,
        value: str,
        icon: str = "\u2022",
        accent: Optional[str] = None,
    ) -> None:
        super().__init__(master, corner_radius=16)
        self.configure(fg_color=THEME.color("surface"))
        self.grid_columnconfigure(0, weight=1)

        accent_color = accent or THEME.color("accent")

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 4))
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME.color("text_muted"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            top,
            text=icon,
            font=ctk.CTkFont(size=22),
            text_color=accent_color,
        ).grid(row=0, column=1, sticky="e")

        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=THEME.color("text"),
            anchor="w",
        )
        self.value_label.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 16))

    def set_value(self, value: str) -> None:
        self.value_label.configure(text=value)


# ---------------------------------------------------------------------------
# Progress ring
# ---------------------------------------------------------------------------
class ProgressRing(Card):
    """A circular progress meter drawn into a CTk canvas."""

    def __init__(
        self,
        master,
        size: int = 140,
        thickness: int = 14,
        value: int = 0,
        label: str = "",
    ) -> None:
        super().__init__(master, corner_radius=18)
        self.size = size
        self.thickness = thickness
        self.value = max(0, min(100, value))
        self.label_text = label

        self.canvas = ctk.CTkCanvas(
            self,
            width=size,
            height=size,
            bg=THEME.color("card"),
            highlightthickness=0,
        )
        self.canvas.pack(padx=16, pady=16)
        self._render()

    def set_value(self, value: int, label: str = "") -> None:
        self.value = max(0, min(100, int(value)))
        if label:
            self.label_text = label
        self._render()

    def _render(self) -> None:
        self.canvas.delete("all")
        cx = cy = self.size // 2
        radius = (self.size - self.thickness) // 2

        # Track
        self.canvas.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            outline=THEME.color("border"),
            width=self.thickness,
        )

        # Progress arc
        if self.value > 0:
            extent = -360 * (self.value / 100.0)
            self.canvas.create_arc(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                start=90,
                extent=extent,
                style="arc",
                outline=THEME.color("accent"),
                width=self.thickness,
            )

        # Centered text
        self.canvas.create_text(
            cx,
            cy - 6,
            text=f"{self.value}%",
            fill=THEME.color("text"),
            font=("Segoe UI", 20, "bold"),
        )
        if self.label_text:
            self.canvas.create_text(
                cx,
                cy + 18,
                text=self.label_text,
                fill=THEME.color("text_muted"),
                font=("Segoe UI", 11),
            )


# ---------------------------------------------------------------------------
# Progress bar
# ---------------------------------------------------------------------------
class ThemedProgressBar(ctk.CTkProgressBar):
    def __init__(self, master, **kwargs) -> None:
        super().__init__(
            master,
            progress_color=kwargs.pop("progress_color", THEME.color("accent")),
            fg_color=kwargs.pop("fg_color", THEME.color("surface_alt")),
            height=kwargs.pop("height", 10),
            corner_radius=kwargs.pop("corner_radius", 8),
            **kwargs,
        )


# ---------------------------------------------------------------------------
# Primary button
# ---------------------------------------------------------------------------
class PrimaryButton(ctk.CTkButton):
    def __init__(self, master, text: str, command: Optional[Callable] = None, **kwargs) -> None:
        super().__init__(
            master,
            text=text,
            command=command,
            corner_radius=kwargs.pop("corner_radius", 12),
            height=kwargs.pop("height", 38),
            font=ctk.CTkFont(
                size=kwargs.pop("font_size", 13),
                weight=kwargs.pop("font_weight", "bold"),
            ),
            fg_color=kwargs.pop("fg_color", THEME.color("accent")),
            hover_color=kwargs.pop("hover_color", THEME.color("accent_hover")),
            text_color=kwargs.pop("text_color", "#FFFFFF"),
            **kwargs,
        )


# ---------------------------------------------------------------------------
# Secondary button
# ---------------------------------------------------------------------------
class SecondaryButton(ctk.CTkButton):
    def __init__(self, master, text: str, command: Optional[Callable] = None, **kwargs) -> None:
        super().__init__(
            master,
            text=text,
            command=command,
            corner_radius=kwargs.pop("corner_radius", 12),
            height=kwargs.pop("height", 36),
            font=ctk.CTkFont(size=kwargs.pop("font_size", 13)),
            fg_color=kwargs.pop("fg_color", THEME.color("surface_alt")),
            hover_color=kwargs.pop("hover_color", THEME.color("border")),
            text_color=kwargs.pop("text_color", THEME.color("text")),
            border_width=kwargs.pop("border_width", 1),
            border_color=kwargs.pop("border_color", THEME.color("border")),
            **kwargs,
        )


# ---------------------------------------------------------------------------
# Section header
# ---------------------------------------------------------------------------
class SectionHeader(ctk.CTkFrame):
    def __init__(self, master, title: str, subtitle: str = "", icon: str = "") -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(1, weight=1)

        if icon:
            ctk.CTkLabel(
                self,
                text=icon,
                font=ctk.CTkFont(size=22),
                text_color=THEME.color("accent"),
            ).grid(row=0, column=0, padx=(0, 8), sticky="w")

        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=THEME.color("text"),
        ).grid(row=0, column=1, sticky="w")

        if subtitle:
            ctk.CTkLabel(
                self,
                text=subtitle,
                font=ctk.CTkFont(size=12),
                text_color=THEME.color("text_muted"),
            ).grid(row=1, column=1, sticky="w", pady=(2, 0))
