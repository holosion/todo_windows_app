"""Settings view - theme, notifications, default values, fonts, etc."""
from __future__ import annotations

import datetime as _dt
from typing import Callable, List, Optional

import customtkinter as ctk
from tkinter import filedialog, messagebox

from ..controllers.backup_controller import BackupController
from ..controllers.category_controller import CategoryController
from ..controllers.settings_controller import SettingsController
from ..controllers.task_controller import TaskController
from ..utils.constants import (
    COLOR_TAGS,
    DEFAULT_CATEGORIES,
    PRIORITIES,
    REPEAT_OPTIONS,
    REMINDER_OPTIONS,
    THEMES,
)
from ..utils.helpers import format_date
from .theme import THEME
from .widgets import Card, PrimaryButton, SecondaryButton, SectionHeader


class SettingsView(ctk.CTkFrame):
    """Application preferences and management."""

    def __init__(
        self,
        master,
        settings_controller: SettingsController,
        category_controller: CategoryController,
        backup_controller: BackupController,
        task_controller: TaskController,
        on_theme_change: Callable[[str], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.settings_controller = settings_controller
        self.category_controller = category_controller
        self.backup_controller = backup_controller
        self.task_controller = task_controller
        self.on_theme_change = on_theme_change
        self._build()
        self._load_values()

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 4))
        SectionHeader(
            header, title="Settings",
            subtitle="Personalize the app and manage your data",
            icon="\u2699\uFE0F",
        ).pack(anchor="w")

        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=24, pady=(4, 16))
        body.grid_columnconfigure((0, 1), weight=1, uniform="col")

        # --- Appearance ---------------------------------------------
        appearance = Card(body)
        appearance.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        SectionHeader(appearance, title="Appearance",
                       subtitle="Theme and visual style", icon="\U0001F319") \
            .pack(anchor="w", padx=20, pady=(18, 8))

        ctk.CTkLabel(appearance, text="Theme", text_color=THEME.color("text_muted"),
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.theme_var = ctk.StringVar(value="Dark")
        theme_row = ctk.CTkFrame(appearance, fg_color="transparent")
        theme_row.pack(anchor="w", padx=20, pady=(2, 12))
        for theme in THEMES:
            ctk.CTkRadioButton(
                theme_row, text=theme, variable=self.theme_var, value=theme,
                command=self._on_theme_change_event,
            ).pack(side="left", padx=6)

        ctk.CTkLabel(appearance, text="Accent color", text_color=THEME.color("text_muted"),
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.accent_var = ctk.StringVar(value=THEME.color("accent"))
        accent_row = ctk.CTkFrame(appearance, fg_color="transparent")
        accent_row.pack(anchor="w", padx=20, pady=(2, 12))
        for color in COLOR_TAGS:
            ctk.CTkRadioButton(
                accent_row, text="", value=color, variable=self.accent_var,
                fg_color=color, hover_color=color, width=24, height=24,
            ).pack(side="left", padx=4)

        ctk.CTkLabel(appearance, text="Font size", text_color=THEME.color("text_muted"),
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.font_size = ctk.CTkSlider(appearance, from_=11, to=18, number_of_steps=7)
        self.font_size.set(13)
        self.font_size.pack(fill="x", padx=20, pady=(2, 12))
        self.font_size_label = ctk.CTkLabel(appearance, text="13 px",
                                             text_color=THEME.color("text_muted"))
        self.font_size_label.pack(anchor="w", padx=20, pady=(0, 12))
        self.font_size.configure(command=lambda v: self.font_size_label.configure(
            text=f"{int(v)} px"
        ))

        # --- Defaults -------------------------------------------------
        defaults = Card(body)
        defaults.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 8))
        SectionHeader(defaults, title="Defaults", subtitle="Used for new tasks",
                       icon="\u2728").pack(anchor="w", padx=20, pady=(18, 8))
        ctk.CTkLabel(defaults, text="Username", text_color=THEME.color("text_muted"),
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.username_entry = ctk.CTkEntry(defaults, height=36, corner_radius=10)
        self.username_entry.pack(fill="x", padx=20, pady=(2, 8))

        ctk.CTkLabel(defaults, text="Default category", text_color=THEME.color("text_muted"),
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.default_category = ctk.CTkComboBox(
            defaults, values=DEFAULT_CATEGORIES, height=36, corner_radius=10
        )
        self.default_category.pack(fill="x", padx=20, pady=(2, 8))

        ctk.CTkLabel(defaults, text="Default priority", text_color=THEME.color("text_muted"),
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.default_priority = ctk.CTkComboBox(
            defaults, values=PRIORITIES, height=36, corner_radius=10
        )
        self.default_priority.pack(fill="x", padx=20, pady=(2, 8))

        ctk.CTkLabel(defaults, text="Default reminder", text_color=THEME.color("text_muted"),
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.default_reminder = ctk.CTkComboBox(
            defaults, values=[r[0] for r in REMINDER_OPTIONS], height=36, corner_radius=10
        )
        self.default_reminder.pack(fill="x", padx=20, pady=(2, 8))

        ctk.CTkLabel(defaults, text="Default repeat", text_color=THEME.color("text_muted"),
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.default_repeat = ctk.CTkComboBox(
            defaults, values=REPEAT_OPTIONS, height=36, corner_radius=10
        )
        self.default_repeat.pack(fill="x", padx=20, pady=(2, 8))

        ctk.CTkLabel(defaults, text="Startup view", text_color=THEME.color("text_muted"),
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        self.startup_view = ctk.CTkComboBox(
            defaults,
            values=["Dashboard", "Tasks", "Planner", "Calendar", "Statistics", "Productivity"],
            height=36, corner_radius=10,
        )
        self.startup_view.pack(fill="x", padx=20, pady=(2, 12))

        # --- Notifications -------------------------------------------
        notifications = Card(body)
        notifications.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=8)
        SectionHeader(notifications, title="Notifications",
                       subtitle="Reminders and feedback", icon="\U0001F514") \
            .pack(anchor="w", padx=20, pady=(18, 8))
        self.notif_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            notifications, text="Enable notifications",
            variable=self.notif_var,
        ).pack(anchor="w", padx=20, pady=2)
        self.sound_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            notifications, text="Play task completion sounds",
            variable=self.sound_var,
        ).pack(anchor="w", padx=20, pady=2)
        self.confetti_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            notifications, text="Confetti when all daily tasks done",
            variable=self.confetti_var,
        ).pack(anchor="w", padx=20, pady=(2, 12))

        # --- Pomodoro ------------------------------------------------
        pomo = Card(body)
        pomo.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=8)
        SectionHeader(pomo, title="Pomodoro", subtitle="Customize your focus cycles",
                       icon="\U0001F345").pack(anchor="w", padx=20, pady=(18, 8))
        self.pomo_work = self._labeled_entry(pomo, "Work duration (minutes)", "25")
        self.pomo_short = self._labeled_entry(pomo, "Short break (minutes)", "5")
        self.pomo_long = self._labeled_entry(pomo, "Long break (minutes)", "15")
        self.pomo_cycles = self._labeled_entry(pomo, "Cycles before long break", "4")

        # --- Backup & Data -------------------------------------------
        backup = Card(body)
        backup.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(8, 0))
        backup.grid_columnconfigure(0, weight=1)
        SectionHeader(backup, title="Backup & Data",
                       subtitle="Export, import, and restore your data",
                       icon="\U0001F4BE").pack(anchor="w", padx=20, pady=(18, 8))

        btn_row = ctk.CTkFrame(backup, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 8))
        PrimaryButton(btn_row, text="  Create Backup", command=self._on_backup_create) \
            .pack(side="left", padx=4)
        SecondaryButton(btn_row, text="  Export DB", command=self._on_export) \
            .pack(side="left", padx=4)
        SecondaryButton(btn_row, text="  Import DB", command=self._on_import) \
            .pack(side="left", padx=4)
        SecondaryButton(btn_row, text="  Reset to Defaults", command=self._on_reset) \
            .pack(side="left", padx=4)

        self.backup_list = ctk.CTkScrollableFrame(backup, fg_color="transparent", height=160)
        self.backup_list.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.backup_list.grid_columnconfigure(0, weight=1)

        # --- Save button ---------------------------------------------
        save_row = ctk.CTkFrame(self, fg_color="transparent")
        save_row.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 16))
        PrimaryButton(save_row, text="  Save Settings", command=self._on_save) \
            .pack(side="right")
        SecondaryButton(save_row, text="  Discard", command=self._load_values) \
            .pack(side="right", padx=8)

    def _labeled_entry(self, parent, label: str, default: str) -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label, text_color=THEME.color("text_muted"),
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
        entry = ctk.CTkEntry(parent, height=36, corner_radius=10)
        entry.insert(0, default)
        entry.pack(fill="x", padx=20, pady=(2, 8))
        return entry

    # ------------------------------------------------------------------
    def _load_values(self) -> None:
        s = self.settings_controller.get_all()
        self.theme_var.set(s.get("theme", "Dark"))
        self.accent_var.set(s.get("accent_color", THEME.color("accent")))
        self.font_size.set(int(s.get("font_size", 13)))
        self.username_entry.delete(0, "end")
        self.username_entry.insert(0, s.get("username", "Akena"))
        self.default_category.set(s.get("default_category", "Personal"))
        self.default_priority.set(s.get("default_priority", "Medium"))
        self.default_repeat.set(s.get("default_repeat", "None"))
        for label, mins in REMINDER_OPTIONS:
            if mins == s.get("default_reminder", 0):
                self.default_reminder.set(label)
                break
        self.startup_view.set(s.get("startup_view", "Dashboard"))
        self.notif_var.set(bool(s.get("notifications_enabled", True)))
        self.sound_var.set(bool(s.get("sound_enabled", True)))
        self.confetti_var.set(bool(s.get("confetti_enabled", True)))
        self.pomo_work.delete(0, "end"); self.pomo_work.insert(0, str(s.get("pomodoro_work", 25)))
        self.pomo_short.delete(0, "end"); self.pomo_short.insert(0, str(s.get("pomodoro_short_break", 5)))
        self.pomo_long.delete(0, "end"); self.pomo_long.insert(0, str(s.get("pomodoro_long_break", 15)))
        self.pomo_cycles.delete(0, "end"); self.pomo_cycles.insert(0, str(s.get("pomodoro_cycles", 4)))
        self._refresh_backup_list()

    def _on_save(self) -> None:
        try:
            reminder = 0
            for label, mins in REMINDER_OPTIONS:
                if label == self.default_reminder.get():
                    reminder = mins
                    break
            self.settings_controller.update({
                "theme": self.theme_var.get(),
                "accent_color": self.accent_var.get(),
                "font_size": int(self.font_size.get()),
                "username": self.username_entry.get().strip() or "Akena",
                "default_category": self.default_category.get(),
                "default_priority": self.default_priority.get(),
                "default_reminder": reminder,
                "default_repeat": self.default_repeat.get(),
                "startup_view": self.startup_view.get(),
                "notifications_enabled": bool(self.notif_var.get()),
                "sound_enabled": bool(self.sound_var.get()),
                "confetti_enabled": bool(self.confetti_var.get()),
                "pomodoro_work": int(self.pomo_work.get() or 25),
                "pomodoro_short_break": int(self.pomo_short.get() or 5),
                "pomodoro_long_break": int(self.pomo_long.get() or 15),
                "pomodoro_cycles": int(self.pomo_cycles.get() or 4),
            })
            self.on_theme_change(self.theme_var.get())
            messagebox.showinfo("Saved", "Settings saved successfully.", parent=self)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error", f"Could not save settings: {exc}", parent=self)

    def _on_theme_change_event(self) -> None:
        # Preview the theme immediately
        self.on_theme_change(self.theme_var.get())

    # ------------------------------------------------------------------
    def _refresh_backup_list(self) -> None:
        for child in self.backup_list.winfo_children():
            child.destroy()
        backups = self.backup_controller.list_backups()
        if not backups:
            ctk.CTkLabel(
                self.backup_list,
                text="No backups yet. Use 'Create Backup' to make one.",
                text_color=THEME.color("text_muted"),
            ).grid(row=0, column=0, padx=10, pady=20)
            return
        for i, b in enumerate(backups):
            row = ctk.CTkFrame(self.backup_list, fg_color=THEME.color("surface_alt"),
                               corner_radius=10)
            row.grid(row=i, column=0, sticky="ew", padx=4, pady=4)
            row.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                row,
                text=f"\U0001F4BE  {b.name}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=THEME.color("text"),
                anchor="w",
            ).grid(row=0, column=0, padx=10, pady=(8, 0), sticky="ew")
            created = (
                b.created_at + _dt.timedelta(hours=3)
                if b.created_at else _dt.datetime.now()
            )
            size_kb = max(1, b.size_bytes // 1024)
            ctk.CTkLabel(
                row,
                text=f"{format_date(created.date())}  •  {size_kb} KB",
                font=ctk.CTkFont(size=11),
                text_color=THEME.color("text_muted"),
                anchor="w",
            ).grid(row=1, column=0, padx=10, pady=(0, 8), sticky="ew")
            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.grid(row=0, column=1, rowspan=2, padx=8, pady=8, sticky="e")
            SecondaryButton(actions, text="Restore", width=80,
                            command=lambda bid=b.id: self._on_restore(bid)).pack(side="left", padx=2)
            SecondaryButton(actions, text="Delete", width=80,
                            command=lambda bid=b.id: self._on_delete_backup(bid)).pack(side="left", padx=2)

    def _on_backup_create(self) -> None:
        self.backup_controller.create_backup(note="manual")
        self._refresh_backup_list()
        messagebox.showinfo("Backup", "Backup created.", parent=self)

    def _on_export(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export database",
            defaultextension=".db",
            filetypes=[("SQLite database", "*.db")],
            initialfile="akena_todo_export.db",
        )
        if not path:
            return
        try:
            self.backup_controller.export_database(path)
            messagebox.showinfo("Exported", f"Database exported to:\n{path}", parent=self)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error", f"Export failed: {exc}", parent=self)

    def _on_import(self) -> None:
        if not messagebox.askyesno(
            "Confirm import",
            "Importing will replace all current data. Continue?",
            parent=self,
        ):
            return
        path = filedialog.askopenfilename(
            title="Select database to import",
            filetypes=[("SQLite database", "*.db")],
        )
        if not path:
            return
        try:
            self.backup_controller.import_database(path)
            messagebox.showinfo("Imported", "Database imported. Please restart the app.",
                                parent=self)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error", f"Import failed: {exc}", parent=self)

    def _on_restore(self, backup_id: int) -> None:
        if not messagebox.askyesno(
            "Confirm restore", "This will replace all current data. Continue?",
            parent=self,
        ):
            return
        if self.backup_controller.restore_backup(backup_id):
            messagebox.showinfo("Restored", "Backup restored. Please restart the app.",
                                parent=self)
        else:
            messagebox.showerror("Error", "Could not restore backup.", parent=self)

    def _on_delete_backup(self, backup_id: int) -> None:
        if not messagebox.askyesno("Confirm", "Delete this backup?", parent=self):
            return
        self.backup_controller.delete_backup(backup_id)
        self._refresh_backup_list()

    def _on_reset(self) -> None:
        if not messagebox.askyesno(
            "Reset settings", "Restore all settings to their defaults?", parent=self
        ):
            return
        self.settings_controller.reset()
        self._load_values()
        self.on_theme_change(self.settings_controller.get("theme", "Dark"))
