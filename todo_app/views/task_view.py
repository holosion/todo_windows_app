"""Task management view - search, filter, sort, and edit tasks."""
from __future__ import annotations

import datetime as _dt
from typing import Callable, List, Optional

import customtkinter as ctk

from ..controllers.task_controller import TaskController
from ..models.task import Task
from ..utils.constants import (
    PRIORITIES,
    PRIORITY_COLORS,
    REMINDER_OPTIONS,
    STATUS_COLORS,
    STATUSES,
)
from ..utils.helpers import (
    format_date,
    format_time,
    humanize_duration,
    is_overdue,
)
from .task_editor import TaskEditorDialog
from .theme import THEME
from .widgets import (
    Card,
    PrimaryButton,
    SecondaryButton,
    SectionHeader,
    ThemedProgressBar,
)


_FILTER_PRESETS = [
    ("All", "all"),
    ("Today", "today"),
    ("Tomorrow", "tomorrow"),
    ("This Week", "this_week"),
    ("This Month", "this_month"),
    ("Completed", "completed"),
    ("Incomplete", "incomplete"),
    ("High Priority", "high_priority"),
    ("Overdue", "overdue"),
    ("Pinned", "pinned"),
    ("Favorites", "favorites"),
    ("Archived", "archived"),
]

_SORT_OPTIONS = [
    ("Custom Order", "custom"),
    ("Due Date", "due_date"),
    ("Priority", "priority"),
    ("Title", "title"),
    ("Status", "status"),
    ("Created", "created_at"),
]


class TaskView(ctk.CTkFrame):
    """Full task management screen: list, filters, search, sort, edit."""

    def __init__(
        self,
        master,
        task_controller: TaskController,
        on_change: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.task_controller = task_controller
        self.on_change = on_change
        self._current_filter = "all"
        self._current_sort = "custom"
        self._descending = False
        self._search_text = ctk.StringVar()
        self._search_text.trace_add("write", lambda *_: self._refresh())

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._build()

    # ------------------------------------------------------------------
    def _build(self) -> None:
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        header.grid_columnconfigure(1, weight=1)

        SectionHeader(
            header, title="Tasks", subtitle="Plan, organize, and conquer your day"
        ).grid(row=0, column=0, sticky="w")
        PrimaryButton(header, text="  New Task", command=self._on_new).grid(
            row=0, column=2, sticky="e"
        )

        # Toolbar (search + sort)
        toolbar = Card(self)
        toolbar.grid(row=1, column=0, sticky="ew", padx=24, pady=8)
        toolbar.grid_columnconfigure(1, weight=1)
        self.search_entry = ctk.CTkEntry(
            toolbar,
            height=36,
            placeholder_text="\U0001F50D  Search by title, description, notes...",
            textvariable=self._search_text,
            corner_radius=10,
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(16, 8), pady=12)
        sort_label = ctk.CTkLabel(toolbar, text="Sort by:", text_color=THEME.color("text_muted"))
        sort_label.grid(row=0, column=2, padx=(8, 4))
        self.sort_combo = ctk.CTkComboBox(
            toolbar,
            values=[label for label, _ in _SORT_OPTIONS],
            width=140, height=36, corner_radius=10,
            command=self._on_sort_change,
        )
        self.sort_combo.set(_SORT_OPTIONS[0][0])
        self.sort_combo.grid(row=0, column=3, padx=4, pady=12)
        self.sort_dir_btn = SecondaryButton(toolbar, text="\u2191 Asc", width=80,
                                            command=self._on_sort_dir)
        self.sort_dir_btn.grid(row=0, column=4, padx=4, pady=12)

        # Filter chips + list
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 16))
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=1)

        filter_bar = ctk.CTkFrame(body, fg_color="transparent")
        filter_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self._filter_buttons: dict[str, ctk.CTkButton] = {}
        for i, (label, key) in enumerate(_FILTER_PRESETS):
            btn = ctk.CTkButton(
                filter_bar,
                text=label,
                height=32,
                corner_radius=16,
                fg_color=THEME.color("surface_alt"),
                hover_color=THEME.color("accent_hover"),
                text_color=THEME.color("text"),
                command=lambda k=key: self._on_filter(k),
            )
            btn.grid(row=0, column=i, padx=4, pady=4)
            self._filter_buttons[key] = btn

        # List card
        list_card = Card(body)
        list_card.grid(row=1, column=0, sticky="nsew")
        list_card.grid_columnconfigure(0, weight=1)
        list_card.grid_rowconfigure(1, weight=1)

        list_header = ctk.CTkFrame(list_card, fg_color="transparent")
        list_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 8))
        list_header.grid_columnconfigure(0, weight=1)
        self.list_title = ctk.CTkLabel(
            list_header,
            text="All Tasks",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=THEME.color("text"),
        )
        self.list_title.grid(row=0, column=0, sticky="w")
        self.list_count = ctk.CTkLabel(
            list_header,
            text="0 tasks",
            text_color=THEME.color("text_muted"),
            font=ctk.CTkFont(size=12),
        )
        self.list_count.grid(row=0, column=1, sticky="e")

        self.scroll = ctk.CTkScrollableFrame(list_card, fg_color="transparent")
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.scroll.grid_columnconfigure(0, weight=1)

        self.empty_label = ctk.CTkLabel(
            self.scroll,
            text="No tasks here. Click \u2795 New Task to get started!",
            text_color=THEME.color("text_muted"),
            font=ctk.CTkFont(size=14),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def refresh(self) -> None:
        self._refresh()

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def _on_new(self) -> None:
        with self.task_controller.db.session() as categories:
            from ..models.category import Category as _Cat
            cats = categories.query(_Cat).all()
        dlg = TaskEditorDialog(
            self.winfo_toplevel(),
            categories=cats,
            defaults=self._default_values(),
            title="New Task",
        )
        data = dlg.show()
        if data is None:
            return
        try:
            task = self.task_controller.create_task(**data)
            self._after_change(task.id)

        except Exception as exc:  # noqa: BLE001
            self._notify(f"Could not create task: {exc}", error=True)

    def _on_filter(self, key: str) -> None:
        self._current_filter = key
        for k, btn in self._filter_buttons.items():
            if k == key:
                btn.configure(fg_color=THEME.color("accent"), text_color="#FFFFFF")
            else:
                btn.configure(fg_color=THEME.color("surface_alt"), text_color=THEME.color("text"))
        self._refresh()

    def _on_sort_change(self, value: str) -> None:
        for label, key in _SORT_OPTIONS:
            if label == value:
                self._current_sort = key
                break
        self._refresh()

    def _on_sort_dir(self) -> None:
        self._descending = not self._descending
        self.sort_dir_btn.configure(text=("\u2193 Desc" if self._descending else "\u2191 Asc"))
        self._refresh()

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------
    def _current_tasks(self) -> List[Task]:
        query = self._search_text.get().strip()
        if self._current_filter == "all":
            tasks = self.task_controller.list_tasks(include_archived=False)
            if query:
                return self.task_controller.search(query)
            return tasks
        tasks = self.task_controller.filter_preset(self._current_filter)
        if query:
            names = {t.id for t in tasks}
            for t in self.task_controller.search(query):
                if t.id not in names:
                    tasks.append(t)
        return tasks

    def _refresh(self) -> None:
        for child in self.scroll.winfo_children():
            child.destroy()
        tasks = self._current_tasks()
        if self._current_sort != "custom":
            tasks = self.task_controller.sort(tasks, self._current_sort, self._descending)

        for label, key in _FILTER_PRESETS:
            if key == self._current_filter:
                self.list_title.configure(text=label)
                break

        self.list_count.configure(text=f"{len(tasks)} task{'s' if len(tasks) != 1 else ''}")

        if not tasks:
            self.empty_label = ctk.CTkLabel(
                self.scroll,
                text="No tasks here. Click \u2795 New Task to get started!",
                text_color=THEME.color("text_muted"),
                font=ctk.CTkFont(size=14),
            )
            self.empty_label.grid(row=0, column=0, padx=20, pady=40)
            return

        for i, task in enumerate(tasks):
            row = self._build_row(task)
            row.grid(row=i, column=0, sticky="ew", padx=4, pady=4)

    def _build_row(self, task: Task) -> ctk.CTkFrame:
        row = Card(self.scroll, corner_radius=12)
        row.grid_columnconfigure(1, weight=1)
        row.configure(fg_color=THEME.color("surface_alt"))

        # Color bar
        ctk.CTkFrame(row, width=6, corner_radius=3, fg_color=task.color_tag or THEME.color("accent")) \
            .grid(row=0, column=0, sticky="ns", padx=(8, 0), pady=8)

        # Checkbox
        completed_var = ctk.BooleanVar(value=task.is_completed())
        chk = ctk.CTkCheckBox(
            row,
            text="",
            width=24,
            variable=completed_var,
            command=lambda t=task: self._on_toggle_complete(t, completed_var.get()),
        )
        chk.grid(row=0, column=0, padx=(20, 6), pady=10, sticky="w")

        # Main info
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.grid(row=0, column=1, sticky="ew", padx=8, pady=10)
        info.grid_columnconfigure(0, weight=1)

        title_row = ctk.CTkFrame(info, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="ew")
        title_row.grid_columnconfigure(0, weight=1)

        title_text = task.title
        title_font = ctk.CTkFont(size=14, weight="bold")
        title_color = THEME.color("text_muted") if task.is_completed() else THEME.color("text")
        ctk.CTkLabel(
            title_row,
            text=("\U0001F4CC " if task.pinned else "")
            + ("\u2B50 " if task.favorite else "")
            + title_text,
            font=title_font,
            text_color=title_color,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        # Status / priority pill
        pill_frame = ctk.CTkFrame(title_row, fg_color="transparent")
        pill_frame.grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(
            pill_frame,
            text=task.priority,
            fg_color=PRIORITY_COLORS.get(task.priority, THEME.color("accent")),
            text_color="#FFFFFF",
            corner_radius=10,
            padx=10, pady=2,
            font=ctk.CTkFont(size=11, weight="bold"),
        ).pack(side="left", padx=2)
        ctk.CTkLabel(
            pill_frame,
            text=task.status,
            fg_color=STATUS_COLORS.get(task.status, THEME.color("text_muted")),
            text_color="#FFFFFF",
            corner_radius=10,
            padx=10, pady=2,
            font=ctk.CTkFont(size=11),
        ).pack(side="left", padx=2)

        # Description
        if task.description:
            ctk.CTkLabel(
                info,
                text=task.description,
                text_color=THEME.color("text_muted"),
                font=ctk.CTkFont(size=12),
                anchor="w",
                wraplength=600,
                justify="left",
            ).grid(row=1, column=0, sticky="ew", pady=(2, 0))

        # Meta line
        meta_parts: List[str] = []
        if task.category:
            meta_parts.append(f"\U0001F3F7 {task.category.name}")
        if task.due_date:
            due = f"Due {format_date(task.due_date)}"
            if task.due_time:
                due += f" {format_time(task.due_time)}"
            if task.is_overdue():
                due = "\u26A0 OVERDUE  " + due
            meta_parts.append(due)
        if task.estimated_duration:
            meta_parts.append(f"\u23F1 {humanize_duration(task.estimated_duration)}")
        if task.repeat and task.repeat != "None":
            meta_parts.append(f"\U0001F501 {task.repeat}")
        if task.reminder_minutes:
            label = next((l for l, m in REMINDER_OPTIONS if m == task.reminder_minutes), "")
            if label and label != "None":
                meta_parts.append(f"\U0001F514 {label}")
        if meta_parts:
            ctk.CTkLabel(
                info,
                text="   ".join(meta_parts),
                text_color=THEME.color("text_muted"),
                font=ctk.CTkFont(size=11),
                anchor="w",
            ).grid(row=2, column=0, sticky="ew", pady=(2, 0))

        # Tags
        if task.tags:
            tags_frame = ctk.CTkFrame(info, fg_color="transparent")
            tags_frame.grid(row=3, column=0, sticky="ew", pady=(2, 0))
            for tag in task.tags.split(","):
                tag = tag.strip()
                if tag:
                    ctk.CTkLabel(
                        tags_frame, text=f"#{tag}",
                        font=ctk.CTkFont(size=10), text_color=THEME.color("accent"),
                        fg_color=THEME.color("surface_alt"), corner_radius=8,
                        padx=6, pady=1,
                    ).pack(side="left", padx=(0, 4))

        # Subtasks
        if task.subtasks:
            done = sum(1 for s in task.subtasks if s.is_done)
            total = len(task.subtasks)
            ctk.CTkLabel(
                info,
                text=f"\u2611 {done}/{total} subtasks",
                text_color=THEME.color("success") if done == total else THEME.color("text_muted"),
                font=ctk.CTkFont(size=11),
                anchor="w",
            ).grid(row=4, column=0, sticky="ew", pady=(2, 0))

        # Progress bar
        if task.progress and not task.is_completed():
            bar = ThemedProgressBar(info, height=6, corner_radius=4)
            bar.set(task.progress / 100.0)
            bar.grid(row=3, column=0, sticky="ew", pady=(6, 0))

        # Action buttons
        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        ctk.CTkButton(
            actions, text="\u270F", width=32, height=32, corner_radius=8,
            fg_color=THEME.color("surface"),
            hover_color=THEME.color("border"),
            text_color=THEME.color("text"),
            command=lambda t=task: self._on_edit(t),
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            actions, text="\u2398", width=32, height=32, corner_radius=8,
            fg_color=THEME.color("surface"),
            hover_color=THEME.color("border"),
            text_color=THEME.color("text"),
            command=lambda t=task: self._on_duplicate(t),
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            actions, text="\U0001F4CC" if not task.pinned else "\u2715", width=32, height=32,
            corner_radius=8, fg_color=THEME.color("surface"),
            hover_color=THEME.color("border"),
            text_color=THEME.color("warning" if not task.pinned else THEME.color("text_muted")),
            command=lambda t=task: self._on_toggle_pin(t),
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            actions, text="\U0001F4E6" if not task.archived else "\u21A9", width=32, height=32,
            corner_radius=8, fg_color=THEME.color("surface"),
            hover_color=THEME.color("border"),
            text_color=THEME.color("accent"),
            command=lambda t=task: self._on_archive(t),
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            actions, text="\U0001F5D1", width=32, height=32, corner_radius=8,
            fg_color=THEME.color("surface"),
            hover_color=THEME.color("danger"),
            text_color=THEME.color("danger"),
            command=lambda t=task: self._on_delete(t),
        ).pack(side="left", padx=2)

        return row

    # ------------------------------------------------------------------
    # Row actions
    # ------------------------------------------------------------------
    def _on_toggle_complete(self, task: Task, value: bool) -> None:
        if value:
            self.task_controller.mark_completed(task.id)
        else:
            self.task_controller.update_task(task.id, status="In Progress", progress=0)
        self._after_change(task.id)

    def _on_edit(self, task: Task) -> None:
        with self.task_controller.db.session() as categories:
            from ..models.category import Category as _Cat
            cats = categories.query(_Cat).all()
        defaults = {
            "title": task.title,
            "description": task.description,
            "notes": task.notes,
            "category": task.category.name if task.category else "",
            "priority": task.priority,
            "status": task.status,
            "repeat": task.repeat,
            "start_date": task.start_date,
            "due_date": task.due_date or _dt.date.today(),
            "due_time": task.due_time,
            "estimated_duration": task.estimated_duration,
            "reminder_minutes": task.reminder_minutes,
            "color_tag": task.color_tag,
            "progress": task.progress,
            "pinned": task.pinned,
            "favorite": task.favorite,
        }
        dlg = TaskEditorDialog(
            self.winfo_toplevel(),
            categories=cats,
            defaults=defaults,
            title="Edit Task",
        )
        data = dlg.show()
        if data is None:
            return
        self.task_controller.update_task(task.id, **data)
        self._after_change(task.id)

    def _on_duplicate(self, task: Task) -> None:
        new_task = self.task_controller.duplicate_task(task.id)
        if new_task:
            self._after_change(new_task.id)

    def _on_toggle_pin(self, task: Task) -> None:
        self.task_controller.toggle_pin(task.id)
        self._after_change(task.id)

    def _on_archive(self, task: Task) -> None:
        if task.archived:
            self.task_controller.restore_task(task.id)
        else:
            self.task_controller.archive_task(task.id)
        self._after_change(task.id)

    def _on_delete(self, task: Task) -> None:
        if not self._confirm(f"Delete task '{task.title}'? This cannot be undone."):
            return
        self.task_controller.delete_task(task.id)
        self._after_change(None)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _default_values(self) -> dict:
        return {
            "category": self.task_controller.db.load_settings().get(
                "default_category", "Personal"
            ),
            "priority": self.task_controller.db.load_settings().get(
                "default_priority", "Medium"
            ),
            "reminder_minutes": self.task_controller.db.load_settings().get(
                "default_reminder", 0
            ),
            "due_date": _dt.date.today(),
        }

    def _after_change(self, _task_id: Optional[int]) -> None:
        self._refresh()
        self.on_change()

    def _confirm(self, message: str) -> bool:
        from tkinter import messagebox
        return bool(messagebox.askyesno("Confirm", message, parent=self))

    def _notify(self, message: str, error: bool = False) -> None:
        from tkinter import messagebox
        if error:
            messagebox.showerror("Error", message, parent=self)
        else:
            messagebox.showinfo("Info", message, parent=self)
