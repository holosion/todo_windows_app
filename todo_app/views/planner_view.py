"""Daily Planner view - shows today's schedule as a vertical timeline."""
from __future__ import annotations

import datetime as _dt
from typing import List

import customtkinter as ctk

from ..controllers.task_controller import TaskController
from ..models.task import Task
from ..utils.constants import STATUS_COLORS
from ..utils.helpers import format_time, humanize_duration
from .theme import THEME
from .widgets import Card, SectionHeader


class PlannerView(ctk.CTkFrame):
    """A vertical timeline of the user's day."""

    def __init__(self, master, task_controller: TaskController) -> None:
        super().__init__(master, fg_color="transparent")
        self.task_controller = task_controller
        self._build()

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 4))
        SectionHeader(
            header,
            title="Daily Planner",
            subtitle="Your day at a glance",
            icon="\u23F0",
        ).pack(anchor="w")

        date_row = ctk.CTkFrame(self, fg_color="transparent")
        date_row.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 8))
        self.date_label = ctk.CTkLabel(
            date_row,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=THEME.color("text"),
        )
        self.date_label.pack(side="left")
        ctk.CTkButton(
            date_row, text="\u25C0  Prev", width=80, height=32,
            command=lambda: self._shift(-1),
        ).pack(side="right", padx=4)
        ctk.CTkButton(
            date_row, text="Today", width=80, height=32,
            fg_color=THEME.color("accent"),
            command=lambda: self._go_today(),
        ).pack(side="right", padx=4)
        ctk.CTkButton(
            date_row, text="Next  \u25B6", width=80, height=32,
            command=lambda: self._shift(1),
        ).pack(side="right", padx=4)

        body = Card(self)
        body.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 16))
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=1)

        self.timeline = ctk.CTkScrollableFrame(body, fg_color="transparent")
        self.timeline.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.timeline.grid_columnconfigure(0, weight=1)

        self.current_date = _dt.date.today()
        self.refresh()

    def _shift(self, days: int) -> None:
        self.current_date = self.current_date + _dt.timedelta(days=days)
        self.refresh()

    def _go_today(self) -> None:
        self.current_date = _dt.date.today()
        self.refresh()

    def refresh(self) -> None:
        self.date_label.configure(
            text=self.current_date.strftime("%A, %B %d, %Y")
        )
        for child in self.timeline.winfo_children():
            child.destroy()
        tasks = [
            t for t in self.task_controller.search(start=self.current_date, end=self.current_date)
            if not t.archived
        ]
        tasks.sort(key=lambda t: t.due_time or _dt.time(23, 59))

        # Generate default 24-hour slots even if empty
        slots = {h: [] for h in range(24)}
        for t in tasks:
            if t.due_time:
                slots[t.due_time.hour].append(t)

        any_block = False
        for hour in range(24):
            block_tasks = slots[hour]
            self._build_slot(hour, block_tasks)
            if block_tasks:
                any_block = True
        if not any_block:
            ctk.CTkLabel(
                self.timeline,
                text="Nothing scheduled for this day. \U0001F60A",
                text_color=THEME.color("text_muted"),
                font=ctk.CTkFont(size=14),
            ).grid(row=0, column=0, padx=20, pady=40)

    def _build_slot(self, hour: int, tasks: List[Task]) -> None:
        row = ctk.CTkFrame(self.timeline, fg_color="transparent")
        row.grid(row=hour, column=0, sticky="ew", padx=8, pady=4)
        row.grid_columnconfigure(1, weight=1)

        # Time column
        time_label = ctk.CTkLabel(
            row,
            text=f"{hour:02d}:00",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME.color("text_muted"),
            width=60, anchor="e",
        )
        time_label.grid(row=0, column=0, padx=(0, 12), sticky="ne", pady=8)

        if not tasks:
            ctk.CTkLabel(
                row,
                text="—",
                text_color=THEME.color("text_muted"),
                font=ctk.CTkFont(size=12),
            ).grid(row=0, column=1, sticky="w", pady=8)
            return

        for t in tasks:
            card = ctk.CTkFrame(
                row, fg_color=THEME.color("surface_alt"), corner_radius=10
            )
            card.grid(row=0, column=1, sticky="ew", pady=2)
            card.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(
                card,
                text=t.color_tag,
                font=ctk.CTkFont(size=18),
                text_color=t.color_tag, width=28,
            ).grid(row=0, column=0, padx=(10, 4), pady=8)

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.grid(row=0, column=1, sticky="ew", padx=4, pady=8)
            info.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                info,
                text=t.title,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=THEME.color("text"),
                anchor="w",
            ).grid(row=0, column=0, sticky="ew")

            meta = []
            if t.due_time:
                meta.append(f"\u23F0 {format_time(t.due_time)}")
            if t.estimated_duration:
                meta.append(f"\u23F1 {humanize_duration(t.estimated_duration)}")
            if t.category:
                meta.append(t.category.name)
            meta.append(t.status)
            ctk.CTkLabel(
                info,
                text="   ".join(meta),
                font=ctk.CTkFont(size=11),
                text_color=THEME.color("text_muted"),
                anchor="w",
            ).grid(row=1, column=0, sticky="ew")

            ctk.CTkLabel(
                card,
                text=t.priority,
                fg_color=STATUS_COLORS.get(t.status, THEME.color("accent")),
                text_color="#FFFFFF",
                corner_radius=10, padx=10, pady=2,
                font=ctk.CTkFont(size=11, weight="bold"),
            ).grid(row=0, column=2, padx=10, pady=8, sticky="e")
