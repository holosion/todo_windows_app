"""Dashboard view - the first screen the user sees after launch."""
from __future__ import annotations

import datetime as _dt
from typing import Callable, List

import customtkinter as ctk

from ..controllers.task_controller import TaskController
from ..models.task import Task
from ..utils.helpers import (
    format_date,
    format_time,
    greeting_for_hour,
    humanize_duration,
)
from ..utils.quotes import QuoteProvider
from .theme import THEME
from .widgets import (
    Card,
    PrimaryButton,
    ProgressRing,
    SectionHeader,
    StatTile,
    ThemedProgressBar,
)


class DashboardView(ctk.CTkFrame):
    """The main dashboard shown on application startup."""

    REFRESH_MS = 30_000

    def __init__(
        self,
        master,
        task_controller: TaskController,
        on_quick_add: Callable[[], None],
        on_open_task: Callable[[int], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.task_controller = task_controller
        self.on_quick_add = on_quick_add
        self.on_open_task = on_open_task

        self._clock_id: str | None = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_body()
        self.refresh()
        self._tick_clock()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------
    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 12))
        header.grid_columnconfigure(0, weight=1)

        self.greeting_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=THEME.color("text"),
        )
        self.greeting_label.grid(row=0, column=0, sticky="w")

        self.subtitle_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=THEME.color("text_muted"),
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        PrimaryButton(
            header,
            text="  Quick Add Task",
            command=self.on_quick_add,
        ).grid(row=0, column=1, rowspan=2, sticky="e", padx=(12, 0))

    def _build_body(self) -> None:
        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 20))
        body.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="col")
        body.grid_rowconfigure(2, weight=1)

        # --- Stats row --------------------------------------------------
        stats = ctk.CTkFrame(body, fg_color="transparent")
        stats.grid(row=0, column=0, columnspan=4, sticky="ew")
        stats.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="col")

        self.completed_tile = StatTile(
            stats,
            "Completed Today",
            "0",
            icon="\u2705",
            accent=THEME.color("success"),
        )
        self.completed_tile.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.remaining_tile = StatTile(
            stats,
            "Remaining",
            "0",
            icon="\u23F3",
            accent=THEME.color("warning"),
        )
        self.remaining_tile.grid(row=0, column=1, sticky="ew", padx=8)

        self.percent_tile = StatTile(
            stats,
            "Today's Progress",
            "0%",
            icon="\U0001F4C8",
            accent=THEME.color("accent"),
        )
        self.percent_tile.grid(row=0, column=2, sticky="ew", padx=8)

        self.streak_tile = StatTile(
            stats,
            "Current Streak",
            "0 days",
            icon="\U0001F525",
            accent=THEME.color("danger"),
        )
        self.streak_tile.grid(row=0, column=3, sticky="ew", padx=(8, 0))

        # --- Progress + Quote row ---------------------------------------
        progress_row = ctk.CTkFrame(body, fg_color="transparent")
        progress_row.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(16, 0))
        progress_row.grid_columnconfigure((0, 1), weight=1, uniform="col")

        # Progress card
        progress_card = Card(progress_row)
        progress_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        SectionHeader(
            progress_card,
            "Daily Progress",
            "Track how much of today is done",
            icon="\U0001F4CA",
        ).pack(anchor="w", padx=20, pady=(18, 4))

        ring_row = ctk.CTkFrame(progress_card, fg_color="transparent")
        ring_row.pack(fill="x", padx=20, pady=(4, 4))

        self.ring = ProgressRing(ring_row, size=160, thickness=16, value=0)
        self.ring.pack(side="left")

        goal_box = ctk.CTkFrame(ring_row, fg_color="transparent")
        goal_box.pack(side="left", fill="both", expand=True, padx=(20, 0))

        self.daily_label = ctk.CTkLabel(
            goal_box,
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=THEME.color("text"),
            anchor="w",
            justify="left",
        )
        self.daily_label.pack(anchor="w", pady=(0, 8))

        self.weekly_label = ctk.CTkLabel(
            goal_box,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=THEME.color("text_muted"),
            anchor="w",
            justify="left",
        )
        self.weekly_label.pack(anchor="w", pady=(0, 4))

        self.monthly_label = ctk.CTkLabel(
            goal_box,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=THEME.color("text_muted"),
            anchor="w",
            justify="left",
        )
        self.monthly_label.pack(anchor="w")

        self.daily_bar = ThemedProgressBar(progress_card)
        self.daily_bar.pack(fill="x", padx=20, pady=(8, 6))
        self.weekly_bar = ThemedProgressBar(
            progress_card, progress_color=THEME.color("success")
        )
        self.weekly_bar.pack(fill="x", padx=20, pady=(0, 6))
        self.monthly_bar = ThemedProgressBar(
            progress_card, progress_color=THEME.color("warning")
        )
        self.monthly_bar.pack(fill="x", padx=20, pady=(0, 18))

        # Quote card
        quote_card = Card(progress_row)
        quote_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        SectionHeader(
            quote_card,
            "Today's Motivation",
            "A new quote every day",
            icon="\U0001F4AC",
        ).pack(anchor="w", padx=20, pady=(18, 4))

        self.quote_text = ctk.CTkLabel(
            quote_card,
            text="",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=THEME.color("text"),
            wraplength=420,
            justify="left",
        )
        self.quote_text.pack(anchor="w", padx=20, pady=(20, 6), fill="x")

        self.quote_author = ctk.CTkLabel(
            quote_card,
            text="",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color=THEME.color("text_muted"),
            justify="left",
        )
        self.quote_author.pack(anchor="w", padx=20, pady=(0, 18), fill="x")

        # --- Deadlines + Activity row -----------------------------------
        bottom_row = ctk.CTkFrame(body, fg_color="transparent")
        bottom_row.grid(row=2, column=0, columnspan=4, sticky="nsew", pady=(16, 0))
        bottom_row.grid_columnconfigure((0, 1), weight=1, uniform="col")
        bottom_row.grid_rowconfigure(1, weight=1)

        # Upcoming deadlines
        deadlines_card = Card(bottom_row)
        deadlines_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), rowspan=2)
        SectionHeader(
            deadlines_card,
            "Upcoming Deadlines",
            "Next things on your plate",
            icon="\u23F0",
        ).pack(anchor="w", padx=20, pady=(18, 4))

        self.deadlines_list = ctk.CTkScrollableFrame(
            deadlines_card, fg_color="transparent", height=220
        )
        self.deadlines_list.pack(fill="both", expand=True, padx=12, pady=(8, 12))

        # Recent activity
        activity_card = Card(bottom_row)
        activity_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0), rowspan=2)
        SectionHeader(
            activity_card,
            "Recent Activity",
            "Your latest actions",
            icon="\U0001F4DD",
        ).pack(anchor="w", padx=20, pady=(18, 4))

        self.activity_list = ctk.CTkScrollableFrame(
            activity_card, fg_color="transparent", height=220
        )
        self.activity_list.pack(fill="both", expand=True, padx=12, pady=(8, 12))

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------
    def refresh(self) -> None:
        now = _dt.datetime.now()
        username = self.task_controller.db.load_settings().get("username", "Akena")
        greeting = greeting_for_hour(now.hour)
        self.greeting_label.configure(text=f"{greeting}, {username} \U0001F44B")
        self.subtitle_label.configure(
            text=now.strftime("%A, %B %d, %Y  •  %I:%M %p")
        )

        progress = self.task_controller.today_progress()
        self.completed_tile.set_value(str(progress["completed"]))
        self.remaining_tile.set_value(str(progress["remaining"]))
        self.percent_tile.set_value(f"{progress['percent']}%")

        streak = self.task_controller.streak()
        self.streak_tile.set_value(f"{streak['current']} days")

        # Daily / weekly / monthly
        daily = self.task_controller.daily_goals()
        weekly = self.task_controller.weekly_goals()
        monthly = self.task_controller.monthly_goals()

        self.ring.set_value(progress["percent"], f"{progress['completed']}/{progress['total']} today")
        self.daily_bar.set(daily["percent"] / 100.0)
        self.weekly_bar.set(weekly["percent"] / 100.0)
        self.monthly_bar.set(monthly["percent"] / 100.0)

        self.daily_label.configure(
            text=(
                f"Daily goal: {daily['completed']}/{daily['goal']}\n"
                f"  {daily['percent']}% of today's target"
            )
        )
        self.weekly_label.configure(
            text=(
                f"Weekly goal: {weekly['completed']}/{weekly['goal']}\n"
                f"  {weekly['percent']}% of this week's target"
            )
        )
        self.monthly_label.configure(
            text=(
                f"Monthly goal: {monthly['completed']}/{monthly['goal']}\n"
                f"  {monthly['percent']}% of this month's target"
            )
        )

        quote, author = QuoteProvider.quote_for_today()
        self.quote_text.configure(text=f"\u201C{quote}\u201D")
        self.quote_author.configure(text=f"— {author}")

        self._refresh_deadlines()
        self._refresh_activity()

    def _refresh_deadlines(self) -> None:
        for child in self.deadlines_list.winfo_children():
            child.destroy()
        deadlines: List[Task] = self.task_controller.upcoming_deadlines(limit=8)
        if not deadlines:
            ctk.CTkLabel(
                self.deadlines_list,
                text="No upcoming deadlines \U0001F389",
                text_color=THEME.color("text_muted"),
                font=ctk.CTkFont(size=13),
            ).pack(anchor="w", padx=8, pady=12)
            return
        for task in deadlines:
            row = self._build_deadline_row(task)
            row.pack(fill="x", padx=4, pady=4)

    def _build_deadline_row(self, task: Task) -> ctk.CTkFrame:
        row = ctk.CTkFrame(self.deadlines_list, fg_color=THEME.color("surface_alt"),
                           corner_radius=10)
        row.grid_columnconfigure(1, weight=1)
        row.bind("<Button-1>", lambda _e, tid=task.id: self.on_open_task(tid))

        ctk.CTkLabel(
            row,
            text=task.color_tag or "\U0001F4CC",
            font=ctk.CTkFont(size=18),
            text_color=task.color_tag,
        ).grid(row=0, column=0, padx=(10, 4), pady=8, sticky="w")

        info = ctk.CTkFrame(row, fg_color="transparent")
        info.grid(row=0, column=1, sticky="ew", padx=4, pady=8)
        info.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            info,
            text=task.title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=THEME.color("text"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew")

        meta_parts = []
        if task.due_date:
            meta_parts.append(format_date(task.due_date))
        if task.due_time:
            meta_parts.append(format_time(task.due_time))
        if task.category:
            meta_parts.append(task.category.name)
        if task.priority:
            meta_parts.append(f"● {task.priority}")
        if task.estimated_duration:
            meta_parts.append(humanize_duration(task.estimated_duration))

        ctk.CTkLabel(
            info,
            text="  •  ".join(meta_parts) or "—",
            font=ctk.CTkFont(size=11),
            text_color=THEME.color("text_muted"),
            anchor="w",
        ).grid(row=1, column=0, sticky="ew")
        return row

    def _refresh_activity(self) -> None:
        from ..models.activity import ActivityLog

        for child in self.activity_list.winfo_children():
            child.destroy()
        with self.task_controller.db.session() as session:
            entries = (
                session.query(ActivityLog)
                .order_by(ActivityLog.created_at.desc())
                .limit(8)
                .all()
            )
        if not entries:
            ctk.CTkLabel(
                self.activity_list,
                text="No activity yet — start by adding a task!",
                text_color=THEME.color("text_muted"),
                font=ctk.CTkFont(size=13),
            ).pack(anchor="w", padx=8, pady=12)
            return
        for entry in entries:
            row = ctk.CTkFrame(
                self.activity_list, fg_color=THEME.color("surface_alt"), corner_radius=10
            )
            row.pack(fill="x", padx=4, pady=4)
            ctk.CTkLabel(
                row,
                text=entry.icon or "•",
                font=ctk.CTkFont(size=16),
                text_color=THEME.color("accent"),
                width=28,
            ).pack(side="left", padx=(8, 0), pady=8)
            text = ctk.CTkLabel(
                row,
                text=entry.description,
                font=ctk.CTkFont(size=12),
                text_color=THEME.color("text"),
                anchor="w",
                justify="left",
            )
            text.pack(side="left", fill="x", expand=True, padx=6, pady=8)

    # ------------------------------------------------------------------
    # Clock
    # ------------------------------------------------------------------
    def _tick_clock(self) -> None:
        now = _dt.datetime.now()
        try:
            self.subtitle_label.configure(
                text=now.strftime("%A, %B %d, %Y  •  %I:%M:%S %p")
            )
        except Exception:
            pass
        self._clock_id = self.after(1000, self._tick_clock)

    def destroy(self) -> None:  # type: ignore[override]
        if self._clock_id is not None:
            try:
                self.after_cancel(self._clock_id)
            except Exception:
                pass
        super().destroy()
