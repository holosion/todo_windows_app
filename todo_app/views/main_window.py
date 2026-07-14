"""Main application window - sidebar + topbar + content area."""
from __future__ import annotations

import datetime as _dt
import os
import sys
from pathlib import Path
from typing import Callable, Dict, Optional

import customtkinter as ctk
from tkinter import messagebox

from ..controllers.activity_controller import ActivityController
from ..controllers.backup_controller import BackupController
from ..controllers.category_controller import CategoryController
from ..controllers.notification_service import NotificationService
from ..controllers.settings_controller import SettingsController
from ..controllers.statistics_controller import StatisticsController
from ..controllers.task_controller import TaskController
from ..database.db_manager import DatabaseManager
from ..models.category import Category
from ..utils.constants import APP_NAME
from ..utils.helpers import greeting_for_hour
from ..utils.logger import get_logger
from . import theme as theme_mod
from .calendar_view import CalendarView
from .confetti import ConfettiOverlay
from .dashboard import DashboardView
from .icons import icon
from .planner_view import PlannerView
from .pomodoro_view import PomodoroView
from .quick_add import QuickAddDialog
from .settings_view import SettingsView
from .stats_view import StatsView
from .task_view import TaskView
from .theme import THEME


class MainWindow(ctk.CTk):
    """The top-level window of the application."""

    NAV_ITEMS = [
        ("dashboard", "Dashboard"),
        ("tasks", "Tasks"),
        ("planner", "Daily Planner"),
        ("calendar", "Calendar"),
        ("stats", "Statistics"),
        ("pomodoro", "Productivity"),
        ("settings", "Settings"),
    ]

    def __init__(self, base_dir: Path) -> None:
        super().__init__()

        self.logger = get_logger("ui")
        self.base_dir = base_dir

        # ---------- Bootstrap controllers ---------------------------
        self.db = DatabaseManager(base_dir / "akena_todo.db")
        self.db.create_all()
        self.task_controller = TaskController(self.db)
        self.category_controller = CategoryController(self.db)
        self.settings_controller = SettingsController(self.db)
        self.statistics_controller = StatisticsController(self.db)
        self.backup_controller = BackupController(self.db, base_dir / "backups")
        self.activity_controller = ActivityController(self.db)
        self.notification_service = NotificationService(
            self.task_controller, on_fire=self._on_system_notification
        )

        # ---------- Apply initial theme -----------------------------
        initial_theme = self.settings_controller.get("theme", "Dark")
        THEME.apply(initial_theme)

        # ---------- Window configuration ---------------------------
        self.title(APP_NAME)
        self.geometry("1280x820")
        self.minsize(1100, 720)
        self.configure(fg_color=THEME.color("bg"))
        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        # ---------- Layout -----------------------------------------
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_topbar()
        self._build_content()
        self._build_statusbar()
        self._register_shortcuts()

        # ---------- Initial state ----------------------------------
        self._views: Dict[str, ctk.CTkFrame] = {}
        self._active_view: Optional[ctk.CTkFrame] = None
        startup = self.settings_controller.get("startup_view", "Dashboard")
        key = startup.lower().split()[0] if startup else "dashboard"
        self._show_view(self._resolve_key(key))

        self._clock_id: Optional[str] = None
        self._tick_clock()
        self._confetti_overlay: Optional[ConfettiOverlay] = None
        self._check_all_tasks_completed()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.notification_service.start(self)

        # Refresh views on focus so the user always sees fresh data
        self.bind("<FocusIn>", lambda _e: self._refresh_all_views())

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_sidebar(self) -> None:
        self.sidebar = ctk.CTkFrame(
            self, width=240, corner_radius=0, fg_color=THEME.color("sidebar"),
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)
        self.sidebar.grid_propagate(False)

        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=20, pady=(24, 24))
        ctk.CTkLabel(
            brand, text="\u2728", font=ctk.CTkFont(size=28),
            text_color=THEME.color("accent"),
        ).pack(side="left")
        ctk.CTkLabel(
            brand, text="Akena Todo", font=ctk.CTkFont(size=18, weight="bold"),
            text_color=THEME.color("text"),
        ).pack(side="left", padx=(8, 0))

        # Nav buttons
        self._nav_buttons: Dict[str, ctk.CTkButton] = {}
        for i, (key, label) in enumerate(self.NAV_ITEMS, start=1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon(key)}   {label}",
                anchor="w",
                height=42,
                corner_radius=10,
                fg_color="transparent",
                hover_color=THEME.color("sidebar_active"),
                text_color=THEME.color("text"),
                font=ctk.CTkFont(size=13),
                command=lambda k=key: self._show_view(self._resolve_key(k)),
            )
            btn.grid(row=i, column=0, sticky="ew", padx=12, pady=4)
            self._nav_buttons[key] = btn

        # Footer / brand line
        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.grid(row=9, column=0, sticky="ew", padx=20, pady=20)
        ctk.CTkLabel(
            footer, text="v1.0.0  •  Offline",
            font=ctk.CTkFont(size=11),
            text_color=THEME.color("text_muted"),
        ).pack(anchor="w")

    def _build_topbar(self) -> None:
        self.topbar = ctk.CTkFrame(
            self, height=64, corner_radius=0, fg_color=THEME.color("topbar"),
        )
        self.topbar.grid(row=0, column=1, sticky="new", padx=0, pady=0)
        self.topbar.grid_columnconfigure(1, weight=1)
        self.topbar.grid_propagate(False)

        # Hamburger / active label
        self.active_label = ctk.CTkLabel(
            self.topbar, text="",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=THEME.color("text"),
        )
        self.active_label.grid(row=0, column=0, padx=(24, 12), pady=18, sticky="w")

        # Search
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._on_global_search())
        self.search_entry = ctk.CTkEntry(
            self.topbar, width=320, height=36, corner_radius=10,
            placeholder_text="\U0001F50D  Search tasks, notes, categories...",
            textvariable=self.search_var,
        )
        self.search_entry.grid(row=0, column=1, padx=12, pady=14, sticky="ew")

        # Quick add
        self.quick_add_btn = ctk.CTkButton(
            self.topbar, text=f"  {icon('add')}  Quick Add",
            height=36, corner_radius=10,
            fg_color=THEME.color("accent"),
            hover_color=THEME.color("accent_hover"),
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_quick_add,
        )
        self.quick_add_btn.grid(row=0, column=2, padx=12, pady=14, sticky="e")

        # Theme toggle
        self.theme_toggle_btn = ctk.CTkButton(
            self.topbar, text=f"  {icon('sun')}",
            width=44, height=36, corner_radius=10,
            fg_color=THEME.color("surface_alt"),
            hover_color=THEME.color("border"),
            text_color=THEME.color("text"),
            command=self._on_toggle_theme,
        )
        self.theme_toggle_btn.grid(row=0, column=3, padx=12, pady=14, sticky="e")

    def _build_content(self) -> None:
        self.content = ctk.CTkFrame(self, fg_color=THEME.color("bg"))
        self.content.grid(row=0, column=1, sticky="nsew", padx=0, pady=(64, 28))
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    def _build_statusbar(self) -> None:
        self.status = ctk.CTkFrame(self, height=28, fg_color=THEME.color("surface"),
                                   corner_radius=0)
        self.status.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status.grid_columnconfigure(1, weight=1)
        self.status.grid_propagate(False)
        self.status_left = ctk.CTkLabel(
            self.status, text="\u2022  Offline  •  All data stored locally",
            font=ctk.CTkFont(size=11),
            text_color=THEME.color("text_muted"),
        )
        self.status_left.grid(row=0, column=0, padx=16, pady=4, sticky="w")
        self.status_right = ctk.CTkLabel(
            self.status, text="", font=ctk.CTkFont(size=11),
            text_color=THEME.color("text_muted"),
        )
        self.status_right.grid(row=0, column=1, padx=16, pady=4, sticky="e")

    # ------------------------------------------------------------------
    # View management
    # ------------------------------------------------------------------
    def _resolve_key(self, key: str) -> str:
        mapping = {
            "dashboard": "dashboard",
            "tasks": "tasks",
            "planner": "planner",
            "calendar": "calendar",
            "stats": "stats",
            "statistics": "stats",
            "pomodoro": "pomodoro",
            "productivity": "pomodoro",
            "settings": "settings",
        }
        return mapping.get(key, "dashboard")

    def _show_view(self, key: str) -> None:
        if self._active_view is not None:
            self._active_view.grid_forget()
        view = self._views.get(key)
        if view is None:
            view = self._create_view(key)
            self._views[key] = view
        view.grid(row=0, column=0, sticky="nsew")
        self._active_view = view
        self._active_view_key = key

        # Highlight nav button
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.configure(
                    fg_color=THEME.color("sidebar_active"),
                    text_color=THEME.color("accent"),
                )
            else:
                btn.configure(fg_color="transparent", text_color=THEME.color("text"))

        for k, label in self.NAV_ITEMS:
            if k == key:
                self.active_label.configure(text=f"{icon(k)}   {label}")
                break
        # Views that benefit from an explicit refresh
        if hasattr(view, "refresh"):
            try:
                view.refresh()
            except Exception:
                pass

    def _create_view(self, key: str) -> ctk.CTkFrame:
        if key == "dashboard":
            return DashboardView(
                self.content, self.task_controller,
                on_quick_add=self._on_quick_add,
                on_open_task=lambda _id: self._show_view("tasks"),
            )
        if key == "tasks":
            return TaskView(
                self.content, self.task_controller,
                on_change=self._refresh_all_views,
            )
        if key == "planner":
            return PlannerView(self.content, self.task_controller)
        if key == "calendar":
            return CalendarView(self.content, self.task_controller)
        if key == "stats":
            return StatsView(self.content, self.statistics_controller, self.task_controller)
        if key == "pomodoro":
            return PomodoroView(
                self.content, self.task_controller, self.settings_controller
            )
        if key == "settings":
            return SettingsView(
                self.content, self.settings_controller,
                self.category_controller, self.backup_controller,
                self.task_controller,
                on_theme_change=self._on_settings_theme_change,
            )
        return DashboardView(
            self.content, self.task_controller,
            on_quick_add=self._on_quick_add,
            on_open_task=lambda _id: self._show_view("tasks"),
        )

    def _refresh_all_views(self) -> None:
        for view in self._views.values():
            if hasattr(view, "refresh"):
                try:
                    view.refresh()
                except Exception:
                    pass

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------
    def _on_quick_add(self) -> None:
        cats = self.category_controller.list_categories()
        defaults = {
            "category": self.settings_controller.get("default_category", "Personal"),
            "priority": self.settings_controller.get("default_priority", "Medium"),
            "reminder_minutes": self.settings_controller.get("default_reminder", 0),
            "due_date": _dt.date.today(),
        }
        dlg = QuickAddDialog(self, cats, defaults=defaults)
        data = dlg.show()
        if data is None:
            return
        try:
            task = self.task_controller.create_task(**data)
            self._refresh_all_views()
            self._check_all_tasks_completed()
            self.status_right.configure(text=f"Added '{task.title}'")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error", f"Could not add task: {exc}", parent=self)

    def _on_global_search(self) -> None:
        query = self.search_var.get().strip()
        if not query:
            return
        results = self.task_controller.search(query)
        if self._active_view_key != "tasks":
            self._show_view("tasks")
        tasks_view = self._views.get("tasks")
        if tasks_view is not None and hasattr(tasks_view, "_refresh"):
            tasks_view._search_text.set(query)
            tasks_view._refresh()

    def _on_toggle_theme(self) -> None:
        new_theme = "Light" if THEME.name == "Dark" else "Dark"
        self.settings_controller.set("theme", new_theme)
        THEME.apply(new_theme)
        self._restyle_app()

    def _on_settings_theme_change(self, theme: str) -> None:
        THEME.apply(theme)
        self._restyle_app()

    def _restyle_app(self) -> None:
        """Reapply the current palette to the live widgets."""
        self.configure(fg_color=THEME.color("bg"))
        self.content.configure(fg_color=THEME.color("bg"))
        self.sidebar.configure(fg_color=THEME.color("sidebar"))
        self.topbar.configure(fg_color=THEME.color("topbar"))
        self.status.configure(fg_color=THEME.color("surface"))
        # Recreate all views so their internal widgets inherit the new palette
        self._views.clear()
        if self._active_view is not None:
            self._active_view.destroy()
        self._active_view = None
        self._show_view(self._active_view_key if hasattr(self, "_active_view_key") else "dashboard")

        # Toggle icon
        self.theme_toggle_btn.configure(
            text=f"  {icon('sun') if THEME.name == 'Dark' else icon('theme')}"
        )

    def _register_shortcuts(self) -> None:
        self.bind_all("<Control-n>", lambda _e: self._on_quick_add())
        self.bind_all("<Control-N>", lambda _e: self._on_quick_add())
        self.bind_all("<Control-s>", lambda _e: self._save_shortcut())
        self.bind_all("<Control-S>", lambda _e: self._save_shortcut())
        self.bind_all("<Control-f>", lambda _e: self._focus_search())
        self.bind_all("<Control-F>", lambda _e: self._focus_search())
        self.bind_all("<Control-d>", lambda _e: self._duplicate_selected())
        self.bind_all("<Control-D>", lambda _e: self._duplicate_selected())
        self.bind_all("<Delete>", lambda _e: self._delete_selected())
        self.bind_all("<space>", lambda _e: self._toggle_selected())
        self.bind_all("<Control-t>", lambda _e: self._on_toggle_theme())
        self.bind_all("<Control-T>", lambda _e: self._on_toggle_theme())

    def _save_shortcut(self) -> None:
        self.status_right.configure(text="Saved")
        # Save is implicit (autosave on every change); this is a UX cue.

    def _focus_search(self) -> None:
        self.search_entry.focus_set()

    def _duplicate_selected(self) -> None:
        tasks_view = self._views.get("tasks")
        if tasks_view and hasattr(tasks_view, "list_title"):
            # No direct selection in this build; the user uses the row button.
            self.status_right.configure(text="Use the duplicate button on a task row")

    def _delete_selected(self) -> None:
        self.status_right.configure(text="Select a task and use its delete button")

    def _toggle_selected(self) -> None:
        self.status_right.configure(text="Use the checkbox on a task to mark complete")

    # ------------------------------------------------------------------
    # Clock
    # ------------------------------------------------------------------
    def _tick_clock(self) -> None:
        now = _dt.datetime.now()
        try:
            username = self.settings_controller.get("username", "Akena")
            greeting = greeting_for_hour(now.hour)
            self.status_right.configure(
                text=f"{greeting}, {username}  •  {now.strftime('%A %I:%M %p')}"
            )
        except Exception:
            pass
        self._clock_id = self.after(60_000, self._tick_clock)

    # ------------------------------------------------------------------
    # Confetti / completion
    # ------------------------------------------------------------------
    def _check_all_tasks_completed(self) -> None:
        progress = self.task_controller.today_progress()
        if (
            self.settings_controller.get("confetti_enabled", True)
            and progress["total"] > 0
            and progress["completed"] == progress["total"]
            and self._confetti_overlay is None
        ):
            self._fire_confetti()

    def _fire_confetti(self) -> None:
        try:
            self._confetti_overlay = ConfettiOverlay(self)
        except Exception as exc:
            self.logger.warning("Confetti failed: %s", exc)
            return
        self.after(ConfettiOverlay.DURATION_MS + 200, self._clear_confetti)

    def _clear_confetti(self) -> None:
        self._confetti_overlay = None

    # ------------------------------------------------------------------
    # Notification callback
    # ------------------------------------------------------------------
    def _on_system_notification(self, title: str, message: str) -> None:
        self.status_right.configure(text=f"\U0001F514 {title}: {message}")

    # ------------------------------------------------------------------
    # Close
    # ------------------------------------------------------------------
    def _on_close(self) -> None:
        try:
            self.notification_service.stop()
        except Exception:
            pass
        self.destroy()

    def destroy(self) -> None:  # type: ignore[override]
        if self._clock_id is not None:
            try:
                self.after_cancel(self._clock_id)
            except Exception:
                pass
        super().destroy()
