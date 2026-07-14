"""Productivity view - Pomodoro, Stopwatch, Countdown, and goals."""
from __future__ import annotations

import datetime as _dt
from typing import Optional

import customtkinter as ctk

from ..controllers.settings_controller import SettingsController
from ..controllers.task_controller import TaskController
from ..models.pomodoro import PomodoroSession
from ..utils.constants import (
    POMODORO_CYCLES_BEFORE_LONG,
    POMODORO_LONG_BREAK,
    POMODORO_SHORT_BREAK,
    POMODORO_WORK,
)
from .theme import THEME
from .widgets import Card, PrimaryButton, SecondaryButton, SectionHeader


class PomodoroView(ctk.CTkFrame):
    """Pomodoro timer, stopwatch, countdown, and goal tracking in one screen."""

    def __init__(
        self,
        master,
        task_controller: TaskController,
        settings_controller: SettingsController,
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.task_controller = task_controller
        self.settings_controller = settings_controller

        # Pomodoro state
        self._mode = "work"          # work | short_break | long_break
        self._cycles = 0
        self._remaining_seconds = self._work_minutes() * 60
        self._timer_id: Optional[str] = None
        self._running = False
        self._timer_started_at: Optional[_dt.datetime] = None

        # Stopwatch / countdown state
        self._sw_running = False
        self._sw_elapsed = 0
        self._sw_last_tick: Optional[float] = None
        self._sw_id: Optional[str] = None

        self._cd_running = False
        self._cd_remaining = 0
        self._cd_last_tick: Optional[float] = None
        self._cd_id: Optional[str] = None

        self._build()
        self._refresh_timer_label()
        self._refresh_goals()

    # ------------------------------------------------------------------
    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=24, pady=(20, 4))
        SectionHeader(
            header, title="Productivity", subtitle="Pomodoro, stopwatch, and goals",
            icon="\U0001F345",
        ).pack(anchor="w")

        # Pomodoro card
        self.pomo_card = Card(self)
        self.pomo_card.grid(row=1, column=0, sticky="nsew", padx=(24, 8), pady=8)
        self.pomo_card.grid_columnconfigure(0, weight=1)
        SectionHeader(
            self.pomo_card, title="Pomodoro Timer", subtitle="25/5 focus cycles",
            icon="\U0001F345",
        ).pack(anchor="w", padx=20, pady=(18, 4))

        self.mode_label = ctk.CTkLabel(
            self.pomo_card,
            text="WORK",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=THEME.color("accent"),
        )
        self.mode_label.pack(pady=(8, 0))

        self.timer_label = ctk.CTkLabel(
            self.pomo_card,
            text="25:00",
            font=ctk.CTkFont(size=56, weight="bold"),
            text_color=THEME.color("text"),
        )
        self.timer_label.pack(pady=(4, 8))

        self.cycle_label = ctk.CTkLabel(
            self.pomo_card, text="Cycle 0 of 4",
            text_color=THEME.color("text_muted"),
            font=ctk.CTkFont(size=12),
        )
        self.cycle_label.pack()

        btn_row = ctk.CTkFrame(self.pomo_card, fg_color="transparent")
        btn_row.pack(pady=12)
        self.start_btn = PrimaryButton(
            btn_row, text="  Start", command=self._on_pomo_start
        )
        self.start_btn.grid(row=0, column=0, padx=4)
        SecondaryButton(btn_row, text="  Pause", command=self._on_pomo_pause) \
            .grid(row=0, column=1, padx=4)
        SecondaryButton(btn_row, text="  Reset", command=self._on_pomo_reset) \
            .grid(row=0, column=2, padx=4)
        SecondaryButton(btn_row, text="  Skip", command=self._on_pomo_skip) \
            .grid(row=0, column=3, padx=4)

        # Stopwatch / countdown card
        self.sw_card = Card(self)
        self.sw_card.grid(row=1, column=1, sticky="nsew", padx=(8, 24), pady=8)
        self.sw_card.grid_columnconfigure(0, weight=1)
        SectionHeader(
            self.sw_card, title="Stopwatch", subtitle="Measure any duration",
            icon="\u23F1\uFE0F",
        ).pack(anchor="w", padx=20, pady=(18, 4))

        self.sw_label = ctk.CTkLabel(
            self.sw_card, text="00:00.0",
            font=ctk.CTkFont(size=44, weight="bold"),
            text_color=THEME.color("text"),
        )
        self.sw_label.pack(pady=(8, 4))
        sw_btn_row = ctk.CTkFrame(self.sw_card, fg_color="transparent")
        sw_btn_row.pack()
        PrimaryButton(sw_btn_row, text="  Start", command=self._on_sw_start) \
            .grid(row=0, column=0, padx=4)
        SecondaryButton(sw_btn_row, text="  Pause", command=self._on_sw_pause) \
            .grid(row=0, column=1, padx=4)
        SecondaryButton(sw_btn_row, text="  Reset", command=self._on_sw_reset) \
            .grid(row=0, column=2, padx=4)

        ctk.CTkLabel(
            self.sw_card, text="Countdown Timer",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=THEME.color("text"),
        ).pack(pady=(16, 4))
        cd_row = ctk.CTkFrame(self.sw_card, fg_color="transparent")
        cd_row.pack()
        self.cd_minutes_entry = ctk.CTkEntry(cd_row, width=80, height=36, corner_radius=10,
                                             placeholder_text="min")
        self.cd_minutes_entry.grid(row=0, column=0, padx=4)
        self.cd_seconds_entry = ctk.CTkEntry(cd_row, width=80, height=36, corner_radius=10,
                                             placeholder_text="sec")
        self.cd_seconds_entry.grid(row=0, column=1, padx=4)
        PrimaryButton(cd_row, text="  Start", command=self._on_cd_start) \
            .grid(row=0, column=2, padx=4)
        SecondaryButton(cd_row, text="  Stop", command=self._on_cd_stop) \
            .grid(row=0, column=3, padx=4)
        self.cd_label = ctk.CTkLabel(
            self.sw_card, text="00:00",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=THEME.color("success"),
        )
        self.cd_label.pack(pady=(8, 12))

        # Goals card
        goals_card = Card(self)
        goals_card.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=24, pady=(8, 16))
        goals_card.grid_columnconfigure((0, 1, 2), weight=1, uniform="col")
        SectionHeader(
            goals_card, title="Goals",
            subtitle="Track your daily, weekly, and monthly targets",
            icon="\U0001F3AF",
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=20, pady=(18, 4))

        # Daily
        daily_frame = ctk.CTkFrame(goals_card, fg_color=THEME.color("surface_alt"),
                                   corner_radius=12)
        daily_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        ctk.CTkLabel(daily_frame, text="Daily", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=THEME.color("text")).pack(anchor="w", padx=12, pady=(12, 0))
        self.daily_label = ctk.CTkLabel(
            daily_frame, text="0 / 0", font=ctk.CTkFont(size=12),
            text_color=THEME.color("text_muted"),
        )
        self.daily_label.pack(anchor="w", padx=12)
        from .widgets import ThemedProgressBar
        self.daily_bar = ThemedProgressBar(daily_frame, height=8)
        self.daily_bar.pack(fill="x", padx=12, pady=(0, 6))
        self.daily_entry = ctk.CTkEntry(daily_frame, height=30, placeholder_text="Goal")
        self.daily_entry.pack(fill="x", padx=12, pady=(0, 12))
        self.daily_entry.bind("<FocusOut>", lambda _e: self._on_save_goals())
        self.daily_entry.bind("<Return>", lambda _e: self._on_save_goals())

        # Weekly
        weekly_frame = ctk.CTkFrame(goals_card, fg_color=THEME.color("surface_alt"),
                                    corner_radius=12)
        weekly_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=10)
        ctk.CTkLabel(weekly_frame, text="Weekly", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=THEME.color("text")).pack(anchor="w", padx=12, pady=(12, 0))
        self.weekly_label = ctk.CTkLabel(
            weekly_frame, text="0 / 0", font=ctk.CTkFont(size=12),
            text_color=THEME.color("text_muted"),
        )
        self.weekly_label.pack(anchor="w", padx=12)
        self.weekly_bar = ThemedProgressBar(weekly_frame, height=8,
                                            progress_color=THEME.color("success"))
        self.weekly_bar.pack(fill="x", padx=12, pady=(0, 6))
        self.weekly_entry = ctk.CTkEntry(weekly_frame, height=30, placeholder_text="Goal")
        self.weekly_entry.pack(fill="x", padx=12, pady=(0, 12))
        self.weekly_entry.bind("<FocusOut>", lambda _e: self._on_save_goals())
        self.weekly_entry.bind("<Return>", lambda _e: self._on_save_goals())

        # Monthly
        monthly_frame = ctk.CTkFrame(goals_card, fg_color=THEME.color("surface_alt"),
                                     corner_radius=12)
        monthly_frame.grid(row=1, column=2, sticky="ew", padx=10, pady=10)
        ctk.CTkLabel(monthly_frame, text="Monthly", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=THEME.color("text")).pack(anchor="w", padx=12, pady=(12, 0))
        self.monthly_label = ctk.CTkLabel(
            monthly_frame, text="0 / 0", font=ctk.CTkFont(size=12),
            text_color=THEME.color("text_muted"),
        )
        self.monthly_label.pack(anchor="w", padx=12)
        self.monthly_bar = ThemedProgressBar(monthly_frame, height=8,
                                             progress_color=THEME.color("warning"))
        self.monthly_bar.pack(fill="x", padx=12, pady=(0, 6))
        self.monthly_entry = ctk.CTkEntry(monthly_frame, height=30, placeholder_text="Goal")
        self.monthly_entry.pack(fill="x", padx=12, pady=(0, 12))
        self.monthly_entry.bind("<FocusOut>", lambda _e: self._on_save_goals())
        self.monthly_entry.bind("<Return>", lambda _e: self._on_save_goals())

        self._load_goal_entries()

    # ------------------------------------------------------------------
    # Pomodoro
    # ------------------------------------------------------------------
    def _work_minutes(self) -> int:
        return int(self.settings_controller.get("pomodoro_work", POMODORO_WORK))

    def _short_break_minutes(self) -> int:
        return int(self.settings_controller.get("pomodoro_short_break", POMODORO_SHORT_BREAK))

    def _long_break_minutes(self) -> int:
        return int(self.settings_controller.get("pomodoro_long_break", POMODORO_LONG_BREAK))

    def _cycles_target(self) -> int:
        return int(self.settings_controller.get("pomodoro_cycles", POMODORO_CYCLES_BEFORE_LONG))

    def _on_pomo_start(self) -> None:
        if self._running:
            return
        self._running = True
        self._timer_started_at = _dt.datetime.utcnow()
        self._tick_pomo()

    def _on_pomo_pause(self) -> None:
        self._running = False
        if self._timer_id is not None:
            try:
                self.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None

    def _on_pomo_reset(self) -> None:
        self._on_pomo_pause()
        self._cycles = 0
        self._mode = "work"
        self._remaining_seconds = self._work_minutes() * 60
        self._refresh_timer_label()

    def _on_pomo_skip(self) -> None:
        self._on_pomo_pause()
        self._advance_mode(completed=False)

    def _tick_pomo(self) -> None:
        if not self._running:
            return
        self._remaining_seconds -= 1
        if self._remaining_seconds <= 0:
            self._on_pomo_finished()
            return
        self._refresh_timer_label()
        self._timer_id = self.after(1000, self._tick_pomo)

    def _on_pomo_finished(self) -> None:
        from ..utils.logger import get_logger
        from ..controllers.task_controller import TaskController  # noqa: F401
        log = get_logger("pomodoro")
        log.info("Pomodoro phase '%s' finished", self._mode)
        # Persist session
        minutes = (
            self._work_minutes() if self._mode == "work"
            else self._short_break_minutes() if self._mode == "short_break"
            else self._long_break_minutes()
        )
        with self.task_controller.db.session() as session:
            session.add(
                PomodoroSession(
                    kind=self._mode,
                    duration_minutes=minutes,
                    ended_at=_dt.datetime.utcnow(),
                    completed=1,
                )
            )
        if self._mode == "work":
            self._cycles += 1
            self._advance_mode(completed=True)
        else:
            self._advance_mode(completed=True)
        self._running = True
        self._timer_id = self.after(500, self._tick_pomo)

    def _advance_mode(self, completed: bool) -> None:
        if self._mode == "work":
            self._mode = "long_break" if (self._cycles % self._cycles_target() == 0 and self._cycles > 0) else "short_break"
        else:
            self._mode = "work"
        if self._mode == "work":
            self._remaining_seconds = self._work_minutes() * 60
        elif self._mode == "short_break":
            self._remaining_seconds = self._short_break_minutes() * 60
        else:
            self._remaining_seconds = self._long_break_minutes() * 60
        self._refresh_timer_label()

    def _refresh_timer_label(self) -> None:
        mins, secs = divmod(max(0, self._remaining_seconds), 60)
        self.timer_label.configure(text=f"{mins:02d}:{secs:02d}")
        labels = {"work": "WORK", "short_break": "SHORT BREAK", "long_break": "LONG BREAK"}
        colors = {
            "work": THEME.color("accent"),
            "short_break": THEME.color("success"),
            "long_break": THEME.color("warning"),
        }
        self.mode_label.configure(
            text=labels.get(self._mode, ""),
            text_color=colors.get(self._mode, THEME.color("text")),
        )
        self.cycle_label.configure(
            text=f"Cycle {self._cycles} of {self._cycles_target()}"
        )

    # ------------------------------------------------------------------
    # Stopwatch
    # ------------------------------------------------------------------
    def _on_sw_start(self) -> None:
        if self._sw_running:
            return
        self._sw_running = True
        self._sw_last_tick = self._now_seconds()
        self._tick_sw()

    def _on_sw_pause(self) -> None:
        self._sw_running = False
        if self._sw_id is not None:
            try:
                self.after_cancel(self._sw_id)
            except Exception:
                pass
            self._sw_id = None

    def _on_sw_reset(self) -> None:
        self._on_sw_pause()
        self._sw_elapsed = 0
        self._refresh_sw_label()

    def _tick_sw(self) -> None:
        if not self._sw_running:
            return
        now = self._now_seconds()
        self._sw_elapsed += now - (self._sw_last_tick or now)
        self._sw_last_tick = now
        self._refresh_sw_label()
        self._sw_id = self.after(100, self._tick_sw)

    def _refresh_sw_label(self) -> None:
        millis = int((self._sw_elapsed - int(self._sw_elapsed)) * 10)
        mins, secs = divmod(int(self._sw_elapsed), 60)
        self.sw_label.configure(text=f"{mins:02d}:{secs:02d}.{millis}")

    # ------------------------------------------------------------------
    # Countdown
    # ------------------------------------------------------------------
    def _on_cd_start(self) -> None:
        if self._cd_running:
            return
        try:
            minutes = int(self.cd_minutes_entry.get() or 0)
        except ValueError:
            minutes = 0
        try:
            seconds = int(self.cd_seconds_entry.get() or 0)
        except ValueError:
            seconds = 0
        self._cd_remaining = minutes * 60 + seconds
        if self._cd_remaining <= 0:
            return
        self._cd_running = True
        self._cd_last_tick = self._now_seconds()
        self._tick_cd()

    def _on_cd_stop(self) -> None:
        self._cd_running = False
        if self._cd_id is not None:
            try:
                self.after_cancel(self._cd_id)
            except Exception:
                pass
            self._cd_id = None
        self._cd_remaining = 0
        self._refresh_cd_label()

    def _tick_cd(self) -> None:
        if not self._cd_running:
            return
        now = self._now_seconds()
        self._cd_remaining -= now - (self._cd_last_tick or now)
        self._cd_last_tick = now
        if self._cd_remaining <= 0:
            self._cd_remaining = 0
            self._cd_running = False
            self._refresh_cd_label()
            self._fire_notification("Countdown finished!", "Time's up \U0001F389")
            return
        self._refresh_cd_label()
        self._cd_id = self.after(200, self._tick_cd)

    def _refresh_cd_label(self) -> None:
        mins, secs = divmod(int(self._cd_remaining), 60)
        self.cd_label.configure(text=f"{mins:02d}:{secs:02d}")

    # ------------------------------------------------------------------
    # Goals
    # ------------------------------------------------------------------
    def _load_goal_entries(self) -> None:
        s = self.settings_controller.get_all()
        self.daily_entry.insert(0, str(s.get("daily_goal", 5)))
        self.weekly_entry.insert(0, str(s.get("weekly_goal", 25)))
        self.monthly_entry.insert(0, str(s.get("monthly_goal", 100)))
        self._refresh_goals()

    def _on_save_goals(self) -> None:
        try:
            daily = int(self.daily_entry.get() or 5)
            weekly = int(self.weekly_entry.get() or 25)
            monthly = int(self.monthly_entry.get() or 100)
        except ValueError:
            return
        self.settings_controller.update({
            "daily_goal": daily, "weekly_goal": weekly, "monthly_goal": monthly,
        })
        self._refresh_goals()

    def _refresh_goals(self) -> None:
        d = self.task_controller.daily_goals()
        w = self.task_controller.weekly_goals()
        m = self.task_controller.monthly_goals()
        self.daily_label.configure(text=f"{d['completed']} / {d['goal']}")
        self.weekly_label.configure(text=f"{w['completed']} / {w['goal']}")
        self.monthly_label.configure(text=f"{m['completed']} / {m['goal']}")
        self.daily_bar.set(d["percent"] / 100.0)
        self.weekly_bar.set(w["percent"] / 100.0)
        self.monthly_bar.set(m["percent"] / 100.0)

    # ------------------------------------------------------------------
    def _fire_notification(self, title: str, message: str) -> None:
        try:
            from plyer import notification
            notification.notify(
                title=title, message=message, app_name="Akena Todo", timeout=5
            )
        except Exception:
            pass

    def _now_seconds(self) -> float:
        return _dt.datetime.utcnow().timestamp()

    def destroy(self) -> None:  # type: ignore[override]
        for attr in ("_timer_id", "_sw_id", "_cd_id"):
            ref = getattr(self, attr, None)
            if ref is not None:
                try:
                    self.after_cancel(ref)
                except Exception:
                    pass
        super().destroy()
