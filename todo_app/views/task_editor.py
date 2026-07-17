"""Task editor dialog - used for both create and edit flows."""
from __future__ import annotations

import datetime as _dt
from typing import Callable, List, Optional

import customtkinter as ctk
from tkcalendar import DateEntry

from ..models.category import Category
from ..models.task import Task
from ..utils.constants import (
    COLOR_TAGS,
    PRIORITIES,
    REMINDER_OPTIONS,
    REPEAT_OPTIONS,
    STATUSES,
)
from ..utils.helpers import parse_date, parse_time
from .theme import THEME
from .widgets import Card, PrimaryButton, SecondaryButton


class TaskEditorDialog(ctk.CTkToplevel):
    """A modal dialog used to create or edit a task."""

    def __init__(
        self,
        master,
        categories: List[Category],
        defaults: Optional[dict] = None,
        title: str = "New Task",
    ) -> None:
        super().__init__(master)
        self.title(title)
        self.geometry("780x820")
        self.minsize(720, 720)
        self.configure(fg_color=THEME.color("bg"))
        self.transient(master)
        self.grab_set()
        self._categories = categories
        self._defaults = defaults or {}
        self._result: Optional[dict] = None
        self._subtask_titles: List[str] = list(defaults.get("subtasks", []) if defaults else [])

        self._build()
        self._populate_defaults()

    # ------------------------------------------------------------------
    def _build(self) -> None:
        outer = ctk.CTkScrollableFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=20, pady=20)
        outer.grid_columnconfigure((0, 1), weight=1, uniform="col")

        # Title
        ctk.CTkLabel(
            outer, text="Title",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME.color("text_muted"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=4)
        self.title_entry = ctk.CTkEntry(outer, height=38, corner_radius=10,
                                        placeholder_text="e.g. Finish project report")
        self.title_entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=(2, 12))

        # Description
        ctk.CTkLabel(
            outer, text="Description",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME.color("text_muted"),
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=4)
        self.description_text = ctk.CTkTextbox(outer, height=70, corner_radius=10)
        self.description_text.grid(row=3, column=0, columnspan=2, sticky="ew", padx=4, pady=(2, 12))

        # Category / Priority
        ctk.CTkLabel(outer, text="Category", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=THEME.color("text_muted")).grid(row=4, column=0, sticky="w", padx=4)
        ctk.CTkLabel(outer, text="Priority", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=THEME.color("text_muted")).grid(row=4, column=1, sticky="w", padx=4)
        cat_names = [c.name for c in self._categories] or ["Personal"]
        self.category_combo = ctk.CTkComboBox(outer, values=cat_names, height=36, corner_radius=10)
        self.category_combo.grid(row=5, column=0, sticky="ew", padx=4, pady=(2, 12))
        self.priority_combo = ctk.CTkComboBox(outer, values=PRIORITIES, height=36, corner_radius=10)
        self.priority_combo.set("Medium")
        self.priority_combo.grid(row=5, column=1, sticky="ew", padx=4, pady=(2, 12))

        # Status / Repeat
        ctk.CTkLabel(outer, text="Status", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=THEME.color("text_muted")).grid(row=6, column=0, sticky="w", padx=4)
        ctk.CTkLabel(outer, text="Repeat", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=THEME.color("text_muted")).grid(row=6, column=1, sticky="w", padx=4)
        self.status_combo = ctk.CTkComboBox(outer, values=STATUSES, height=36, corner_radius=10)
        self.status_combo.set("Not Started")
        self.status_combo.grid(row=7, column=0, sticky="ew", padx=4, pady=(2, 12))
        self.repeat_combo = ctk.CTkComboBox(outer, values=REPEAT_OPTIONS, height=36, corner_radius=10)
        self.repeat_combo.set("None")
        self.repeat_combo.grid(row=7, column=1, sticky="ew", padx=4, pady=(2, 12))

        # Dates
        ctk.CTkLabel(outer, text="Start Date", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=THEME.color("text_muted")).grid(row=8, column=0, sticky="w", padx=4)
        ctk.CTkLabel(outer, text="Due Date", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=THEME.color("text_muted")).grid(row=8, column=1, sticky="w", padx=4)

        date_row = ctk.CTkFrame(outer, fg_color="transparent")
        date_row.grid(row=9, column=0, columnspan=2, sticky="ew", padx=4, pady=(2, 12))
        date_row.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self.start_date = DateEntry(date_row, width=12, date_pattern="yyyy-mm-dd",
                                    background=THEME.color("accent"), foreground="white", borderwidth=0)
        self.start_date.grid(row=0, column=0, sticky="ew", padx=2)
        ctk.CTkButton(date_row, text="Clear", width=60, height=28,
                      command=lambda: self.start_date.set_date(_dt.date.today())).grid(row=0, column=1, padx=4)

        self.due_date = DateEntry(date_row, width=12, date_pattern="yyyy-mm-dd",
                                  background=THEME.color("accent"), foreground="white", borderwidth=0)
        self.due_date.grid(row=0, column=2, sticky="ew", padx=2)
        ctk.CTkButton(date_row, text="Clear", width=60, height=28,
                      command=lambda: self.due_date.set_date(_dt.date.today())).grid(row=0, column=3, padx=4)

        ctk.CTkLabel(date_row, text="Time").grid(row=0, column=4, padx=(8, 4))
        self.due_time = ctk.CTkEntry(date_row, placeholder_text="HH:MM", width=80)
        self.due_time.grid(row=0, column=5, sticky="ew", padx=2)

        # Duration + Reminder
        ctk.CTkLabel(outer, text="Estimated Duration (minutes)", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=THEME.color("text_muted")).grid(row=10, column=0, sticky="w", padx=4)
        ctk.CTkLabel(outer, text="Reminder", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=THEME.color("text_muted")).grid(row=10, column=1, sticky="w", padx=4)
        self.duration_entry = ctk.CTkEntry(outer, height=36, corner_radius=10, placeholder_text="e.g. 60")
        self.duration_entry.grid(row=11, column=0, sticky="ew", padx=4, pady=(2, 12))
        reminder_labels = [r[0] for r in REMINDER_OPTIONS]
        self.reminder_combo = ctk.CTkComboBox(outer, values=reminder_labels, height=36, corner_radius=10)
        self.reminder_combo.set("None")
        self.reminder_combo.grid(row=11, column=1, sticky="ew", padx=4, pady=(2, 12))

        # Color tag + Progress
        ctk.CTkLabel(outer, text="Color Tag", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=THEME.color("text_muted")).grid(row=12, column=0, sticky="w", padx=4)
        ctk.CTkLabel(outer, text="Progress (%)", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=THEME.color("text_muted")).grid(row=12, column=1, sticky="w", padx=4)

        self.color_var = ctk.StringVar(value=COLOR_TAGS[0])
        color_row = ctk.CTkFrame(outer, fg_color="transparent")
        color_row.grid(row=13, column=0, sticky="ew", padx=4, pady=(2, 12))
        for color in COLOR_TAGS:
            ctk.CTkRadioButton(color_row, text="", value=color, variable=self.color_var,
                               fg_color=color, hover_color=color, width=22, height=22).pack(side="left", padx=2)

        self.progress_slider = ctk.CTkSlider(outer, from_=0, to=100, number_of_steps=20)
        self.progress_slider.set(0)
        self.progress_label = ctk.CTkLabel(outer, text="0%")
        self.progress_slider.grid(row=13, column=1, sticky="ew", padx=4, pady=(2, 12))
        self.progress_label.grid(row=14, column=1, sticky="e", padx=4)
        self.progress_slider.configure(command=self._on_slider_change)

        # Tags
        ctk.CTkLabel(outer, text="Tags (comma-separated)", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=THEME.color("text_muted")).grid(row=15, column=0, columnspan=2, sticky="w", padx=4)
        self.tags_entry = ctk.CTkEntry(outer, height=36, corner_radius=10,
                                       placeholder_text="e.g. urgent, backend, api")
        self.tags_entry.grid(row=16, column=0, columnspan=2, sticky="ew", padx=4, pady=(2, 12))

        # Subtasks
        ctk.CTkLabel(outer, text="Subtasks", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=THEME.color("text_muted")).grid(row=17, column=0, columnspan=2, sticky="w", padx=4)
        subtask_header = ctk.CTkFrame(outer, fg_color="transparent")
        subtask_header.grid(row=18, column=0, columnspan=2, sticky="ew", padx=4, pady=(2, 4))
        self.subtask_entry = ctk.CTkEntry(subtask_header, height=32, corner_radius=8,
                                          placeholder_text="Type a subtask and press Add")
        self.subtask_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(subtask_header, text="Add", width=60, height=32, corner_radius=8,
                      fg_color=THEME.color("accent"), hover_color=THEME.color("accent_hover"),
                      text_color="#FFFFFF", command=self._on_add_subtask).pack(side="right")
        self.subtask_list = ctk.CTkFrame(outer, fg_color="transparent")
        self.subtask_list.grid(row=19, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 12))
        self.subtask_entry.bind("<Return>", lambda _e: self._on_add_subtask())

        # Notes
        ctk.CTkLabel(outer, text="Notes", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=THEME.color("text_muted")).grid(row=20, column=0, columnspan=2, sticky="w", padx=4)
        self.notes_text = ctk.CTkTextbox(outer, height=80, corner_radius=10)
        self.notes_text.grid(row=21, column=0, columnspan=2, sticky="ew", padx=4, pady=(2, 12))

        # Toggles
        toggles = ctk.CTkFrame(outer, fg_color="transparent")
        toggles.grid(row=22, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 12))
        self.pinned_var = ctk.BooleanVar(value=False)
        self.favorite_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(toggles, text="Pinned", variable=self.pinned_var).pack(side="left", padx=6)
        ctk.CTkCheckBox(toggles, text="Favorite", variable=self.favorite_var).pack(side="left", padx=6)

        # Buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 20))
        btn_row.grid_columnconfigure((0, 1), weight=1)
        SecondaryButton(btn_row, text="Cancel", command=self._on_cancel).grid(
            row=0, column=0, sticky="ew", padx=(0, 6))
        PrimaryButton(btn_row, text="Save Task", command=self._on_save).grid(
            row=0, column=1, sticky="ew", padx=(6, 0))

        self.bind("<Escape>", lambda _e: self._on_cancel())
        self.bind("<Control-Return>", lambda _e: self._on_save())

    # ------------------------------------------------------------------
    def _on_add_subtask(self) -> None:
        text = self.subtask_entry.get().strip()
        if not text:
            return
        self._subtask_titles.append(text)
        self.subtask_entry.delete(0, "end")
        self._refresh_subtask_list()

    def _on_remove_subtask(self, idx: int) -> None:
        if 0 <= idx < len(self._subtask_titles):
            self._subtask_titles.pop(idx)
            self._refresh_subtask_list()

    def _refresh_subtask_list(self) -> None:
        for child in self.subtask_list.winfo_children():
            child.destroy()
        for i, title in enumerate(self._subtask_titles):
            row = ctk.CTkFrame(self.subtask_list, fg_color=THEME.color("surface_alt"), corner_radius=8)
            row.pack(fill="x", padx=2, pady=2)
            ctk.CTkLabel(row, text=f"  {i+1}. {title}", font=ctk.CTkFont(size=12),
                         text_color=THEME.color("text"), anchor="w").pack(side="left", fill="x", expand=True, padx=4, pady=4)
            ctk.CTkButton(row, text="\u2715", width=28, height=28, corner_radius=6,
                          fg_color="transparent", hover_color=THEME.color("danger"),
                          text_color=THEME.color("danger"),
                          command=lambda idx=i: self._on_remove_subtask(idx)).pack(side="right", padx=4, pady=4)

    def _on_slider_change(self, value) -> None:
        self.progress_label.configure(text=f"{int(value)}%")

    def _populate_defaults(self) -> None:
        d = self._defaults
        if not d:
            return
        if d.get("title"):
            self.title_entry.insert(0, d["title"])
        if d.get("description"):
            self.description_text.insert("1.0", d["description"])
        if d.get("notes"):
            self.notes_text.insert("1.0", d["notes"])
        if d.get("category"):
            self.category_combo.set(d["category"])
        if d.get("priority"):
            self.priority_combo.set(d["priority"])
        if d.get("status"):
            self.status_combo.set(d["status"])
        if d.get("repeat"):
            self.repeat_combo.set(d["repeat"])
        if d.get("start_date"):
            self.start_date.set_date(d["start_date"])
        if d.get("due_date"):
            self.due_date.set_date(d["due_date"])
        if d.get("due_time"):
            self.due_time.insert(0, d["due_time"].strftime("%H:%M"))
        if d.get("estimated_duration"):
            self.duration_entry.insert(0, str(d["estimated_duration"]))
        if d.get("reminder_minutes") is not None:
            for label, mins in REMINDER_OPTIONS:
                if mins == d["reminder_minutes"]:
                    self.reminder_combo.set(label)
                    break
        if d.get("color_tag"):
            self.color_var.set(d["color_tag"])
        if d.get("progress") is not None:
            self.progress_slider.set(d["progress"])
            self.progress_label.configure(text=f"{int(d['progress'])}%")
        if d.get("pinned"):
            self.pinned_var.set(True)
        if d.get("favorite"):
            self.favorite_var.set(True)
        if d.get("tags"):
            self.tags_entry.insert(0, d["tags"])
        if d.get("subtasks"):
            self._subtask_titles = list(d["subtasks"])
            self._refresh_subtask_list()

    def _on_save(self) -> None:
        title = self.title_entry.get().strip()
        if not title:
            self._flash(self.title_entry, "Title is required")
            return
        reminder_label = self.reminder_combo.get()
        reminder_mins = 0
        for label, mins in REMINDER_OPTIONS:
            if label == reminder_label:
                reminder_mins = mins
                break
        try:
            duration = int(self.duration_entry.get()) if self.duration_entry.get() else None
        except ValueError:
            duration = None
        self._result = {
            "title": title,
            "description": self.description_text.get("1.0", "end").strip(),
            "notes": self.notes_text.get("1.0", "end").strip(),
            "category": self.category_combo.get(),
            "priority": self.priority_combo.get(),
            "status": self.status_combo.get(),
            "repeat": self.repeat_combo.get(),
            "start_date": self.start_date.get_date(),
            "due_date": self.due_date.get_date(),
            "due_time": parse_time(self.due_time.get()),
            "estimated_duration": duration,
            "reminder_minutes": reminder_mins,
            "color_tag": self.color_var.get(),
            "progress": int(self.progress_slider.get()),
            "pinned": self.pinned_var.get(),
            "favorite": self.favorite_var.get(),
            "tags": self.tags_entry.get().strip(),
            "subtask_titles": list(self._subtask_titles),
        }
        self.grab_release()
        self.destroy()

    def _on_cancel(self) -> None:
        self._result = None
        self.grab_release()
        self.destroy()

    def _flash(self, widget, _msg: str) -> None:
        original = widget.cget("border_color")
        widget.configure(border_color=THEME.color("danger"), border_width=2)
        widget.after(1500, lambda: widget.configure(border_color=original, border_width=0))

    def show(self) -> Optional[dict]:
        self.wait_window()
        return self._result
