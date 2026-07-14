"""Calendar view - tkcalendar widget + per-day task list."""
from __future__ import annotations

import datetime as _dt
from typing import List

import customtkinter as ctk
from tkcalendar import Calendar

from ..controllers.task_controller import TaskController
from ..models.task import Task
from ..utils.constants import PRIORITY_COLORS, STATUS_COLORS
from ..utils.helpers import format_time, humanize_duration
from .theme import THEME
from .widgets import Card, SectionHeader


class CalendarView(ctk.CTkFrame):
    """Month calendar with a side panel of selected-day tasks."""

    def __init__(self, master, task_controller: TaskController) -> None:
        super().__init__(master, fg_color="transparent")
        self.task_controller = task_controller
        self._selected_date: _dt.date = _dt.date.today()
        self._build()
        self.refresh()

    def _build(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Calendar card
        cal_card = Card(self)
        cal_card.grid(row=0, column=0, sticky="nsew", padx=(24, 8), pady=20)
        cal_card.grid_columnconfigure(0, weight=1)
        cal_card.grid_rowconfigure(1, weight=1)
        SectionHeader(
            cal_card, title="Calendar", subtitle="Click a day to view its tasks",
            icon="\U0001F4C5",
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 8))

        # Build tkcalendar with palette matching current theme
        bg = THEME.color("bg")
        fg = THEME.color("text")
        sel_bg = THEME.color("accent")
        self.cal = Calendar(
            cal_card,
            selectmode="day",
            year=_dt.date.today().year,
            month=_dt.date.today().month,
            day=_dt.date.today().day,
            date_pattern="yyyy-mm-dd",
            background=sel_bg,
            foreground="white",
            bordercolor=THEME.color("border"),
            headersbackground=sel_bg,
            headersforeground="white",
            normalbackground=THEME.color("surface"),
            normalforeground=fg,
            weekendbackground=THEME.color("surface_alt"),
            weekendforeground=fg,
            othermonthbackground=bg,
            othermonthforeground=THEME.color("text_muted"),
            othermonthwebackground=bg,
            othermonthweforeground=THEME.color("text_muted"),
            selectbackground=sel_bg,
            selectforeground="white",
            font=("Segoe UI", 11),
        )
        self.cal.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 18))
        self.cal.bind("<<CalendarSelected>>", self._on_date_select)

        # Selected day panel
        day_card = Card(self)
        day_card.grid(row=0, column=1, sticky="nsew", padx=(8, 24), pady=20)
        day_card.grid_columnconfigure(0, weight=1)
        day_card.grid_rowconfigure(3, weight=1)
        SectionHeader(
            day_card, title="Day Details", subtitle="Tasks for the selected day",
            icon="\U0001F4C6",
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 4))
        self.selected_label = ctk.CTkLabel(
            day_card,
            text="",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=THEME.color("text"),
        )
        self.selected_label.grid(row=1, column=0, sticky="w", padx=20, pady=(4, 4))
        self.summary_label = ctk.CTkLabel(
            day_card, text="",
            font=ctk.CTkFont(size=12),
            text_color=THEME.color("text_muted"),
        )
        self.summary_label.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 8))

        self.task_list = ctk.CTkScrollableFrame(day_card, fg_color="transparent")
        self.task_list.grid(row=3, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.task_list.grid_columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    def _on_date_select(self, _event=None) -> None:
        try:
            self._selected_date = self.cal.selection_get()
        except Exception:
            return
        self.refresh()

    def refresh(self) -> None:
        for child in self.task_list.winfo_children():
            child.destroy()

        try:
            self._selected_date = self.cal.selection_get()
        except Exception:
            self._selected_date = _dt.date.today()

        self.selected_label.configure(
            text=self._selected_date.strftime("%A, %B %d, %Y")
        )

        tasks = self.task_controller.search(
            start=self._selected_date, end=self._selected_date
        )
        tasks = [t for t in tasks if not t.archived]
        tasks.sort(key=lambda t: (t.due_time or _dt.time(23, 59), t.priority))

        completed = sum(1 for t in tasks if t.is_completed())
        self.summary_label.configure(
            text=f"{len(tasks)} task{'s' if len(tasks) != 1 else ''}  •  "
                 f"{completed} completed  •  {len(tasks) - completed} open"
        )

        if not tasks:
            ctk.CTkLabel(
                self.task_list,
                text="No tasks scheduled for this day \U0001F389",
                text_color=THEME.color("text_muted"),
                font=ctk.CTkFont(size=14),
            ).grid(row=0, column=0, padx=20, pady=40)
            return

        for i, t in enumerate(tasks):
            self._build_task_row(t, i)

    def _build_task_row(self, task: Task, index: int) -> None:
        row = ctk.CTkFrame(self.task_list, fg_color=THEME.color("surface_alt"),
                           corner_radius=10)
        row.grid(row=index, column=0, sticky="ew", padx=4, pady=4)
        row.grid_columnconfigure(1, weight=1)
        ctk.CTkFrame(row, width=6, fg_color=task.color_tag, corner_radius=3) \
            .grid(row=0, column=0, sticky="ns", padx=(8, 0), pady=8)
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.grid(row=0, column=1, sticky="ew", padx=8, pady=8)
        info.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            info,
            text=("\u2705 " if task.is_completed() else "")
            + ("\U0001F4CC " if task.pinned else "")
            + task.title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=THEME.color("text"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew")
        meta = []
        if task.due_time:
            meta.append(f"\u23F0 {format_time(task.due_time)}")
        if task.estimated_duration:
            meta.append(f"\u23F1 {humanize_duration(task.estimated_duration)}")
        if task.category:
            meta.append(f"\U0001F3F7 {task.category.name}")
        meta.append(task.priority)
        ctk.CTkLabel(
            info, text="   ".join(meta),
            text_color=THEME.color("text_muted"),
            font=ctk.CTkFont(size=11),
            anchor="w",
        ).grid(row=1, column=0, sticky="ew")
        ctk.CTkLabel(
            row, text=task.status,
            fg_color=STATUS_COLORS.get(task.status, THEME.color("text_muted")),
            text_color="#FFFFFF",
            corner_radius=10, padx=8, pady=2,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).grid(row=0, column=2, padx=8, pady=8)
