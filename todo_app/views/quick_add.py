"""Quick add task dialog - a small popup for fast task capture."""
from __future__ import annotations

import datetime as _dt
from typing import Callable, List, Optional

import customtkinter as ctk
from tkcalendar import DateEntry

from ..models.category import Category
from ..utils.constants import PRIORITIES, REMINDER_OPTIONS
from ..utils.helpers import parse_time
from .theme import THEME
from .widgets import PrimaryButton, SecondaryButton


class QuickAddDialog(ctk.CTkToplevel):
    """A minimal popup to add a task in seconds."""

    def __init__(
        self,
        master,
        categories: List[Category],
        defaults: Optional[dict] = None,
    ) -> None:
        super().__init__(master)
        self.title("Quick Add Task")
        self.geometry("540x520")
        self.minsize(520, 480)
        self.configure(fg_color=THEME.color("bg"))
        self.transient(master)
        self.grab_set()
        self._categories = categories
        self._defaults = defaults or {}
        self._result: Optional[dict] = None
        self._build()
        self._populate()
        self.after(50, lambda: self.title_entry.focus_set())
        self.bind("<Escape>", lambda _e: self._on_cancel())
        self.bind("<Control-Return>", lambda _e: self._on_save())

    def _build(self) -> None:
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame, text="What needs to be done?",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=THEME.color("text"),
        ).grid(row=0, column=0, sticky="w", padx=4, pady=(0, 4))

        self.title_entry = ctk.CTkEntry(
            frame, height=40, corner_radius=10,
            placeholder_text="e.g. Submit assignment",
        )
        self.title_entry.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 12))

        # Quick options row
        opt_row = ctk.CTkFrame(frame, fg_color="transparent")
        opt_row.grid(row=2, column=0, sticky="ew", padx=4, pady=(0, 8))
        opt_row.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(opt_row, text="Priority", text_color=THEME.color("text_muted"),
                     font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=4)
        ctk.CTkLabel(opt_row, text="Category", text_color=THEME.color("text_muted"),
                     font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, sticky="w", padx=4)
        ctk.CTkLabel(opt_row, text="Reminder", text_color=THEME.color("text_muted"),
                     font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, sticky="w", padx=4)

        self.priority_combo = ctk.CTkComboBox(opt_row, values=PRIORITIES, height=36, corner_radius=10)
        self.priority_combo.set("Medium")
        self.priority_combo.grid(row=1, column=0, sticky="ew", padx=4, pady=(2, 8))

        cat_names = [c.name for c in self._categories] or ["Personal"]
        self.category_combo = ctk.CTkComboBox(opt_row, values=cat_names, height=36, corner_radius=10)
        self.category_combo.grid(row=1, column=1, sticky="ew", padx=4, pady=(2, 8))

        self.reminder_combo = ctk.CTkComboBox(
            opt_row, values=[r[0] for r in REMINDER_OPTIONS], height=36, corner_radius=10
        )
        self.reminder_combo.set("None")
        self.reminder_combo.grid(row=1, column=2, sticky="ew", padx=4, pady=(2, 8))

        # Date / time
        date_row = ctk.CTkFrame(frame, fg_color="transparent")
        date_row.grid(row=3, column=0, sticky="ew", padx=4, pady=(0, 8))
        date_row.grid_columnconfigure((0, 1, 2, 3), weight=1)
        ctk.CTkLabel(date_row, text="Date", text_color=THEME.color("text_muted"),
                     font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=4)
        ctk.CTkLabel(date_row, text="Time", text_color=THEME.color("text_muted"),
                     font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, sticky="w", padx=4)
        ctk.CTkLabel(date_row, text="Duration (min)", text_color=THEME.color("text_muted"),
                     font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, sticky="w", padx=4)

        self.date_entry = DateEntry(
            date_row, width=12, date_pattern="yyyy-mm-dd",
            background=THEME.color("accent"), foreground="white", borderwidth=0
        )
        self.date_entry.grid(row=1, column=0, sticky="ew", padx=4, pady=(2, 8))
        self.time_entry = ctk.CTkEntry(date_row, placeholder_text="HH:MM", height=36)
        self.time_entry.grid(row=1, column=1, sticky="ew", padx=4, pady=(2, 8))
        self.duration_entry = ctk.CTkEntry(date_row, placeholder_text="60", height=36)
        self.duration_entry.grid(row=1, column=2, sticky="ew", padx=4, pady=(2, 8))

        # Notes
        self.notes_text = ctk.CTkTextbox(frame, height=80, corner_radius=10)
        self.notes_text.grid(row=4, column=0, sticky="nsew", padx=4, pady=(0, 8))
        frame.grid_rowconfigure(4, weight=1)

        # Buttons
        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.grid(row=5, column=0, sticky="ew", padx=4, pady=(8, 0))
        btn_row.grid_columnconfigure((0, 1), weight=1)
        SecondaryButton(btn_row, text="Cancel", command=self._on_cancel) \
            .grid(row=0, column=0, sticky="ew", padx=(0, 4))
        PrimaryButton(btn_row, text="Add Task", command=self._on_save) \
            .grid(row=0, column=1, sticky="ew", padx=(4, 0))

def _populate(self) -> None:
        d = self._defaults
        if d.get("category"):
            self.category_combo.set(d["category"])
        if d.get("priority"):
            self.priority_combo.set(d["priority"])
        if d.get("due_date"):
            self.date_entry.set_date(d["due_date"])
        if d.get("due_time"):
            # due_time expected as datetime.time object
            self.time_entry.delete(0, "end")
            self.time_entry.insert(0, d["due_time"].strftime("%H:%M"))
        if d.get("estimated_duration") is not None:
            self.duration_entry.delete(0, "end")
            self.duration_entry.insert(0, str(d["estimated_duration"]))
        for label, mins in REMINDER_OPTIONS:
            if mins == d.get("reminder_minutes", 0):
                self.reminder_combo.set(label)
                break

    def _on_save(self) -> None:
        title = self.title_entry.get().strip()
        if not title:
            self.title_entry.configure(border_color=THEME.color("danger"), border_width=2)
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
            "category": self.category_combo.get(),
            "priority": self.priority_combo.get(),
            "due_date": self.date_entry.get_date(),
            "due_time": parse_time(self.time_entry.get()),
            "estimated_duration": duration,
            "reminder_minutes": reminder_mins,
            "notes": self.notes_text.get("1.0", "end").strip(),
        }
        self.grab_release()
        self.destroy()

    def _on_cancel(self) -> None:
        self._result = None
        self.grab_release()
        self.destroy()

    def show(self) -> Optional[dict]:
        self.wait_window()
        return self._result
