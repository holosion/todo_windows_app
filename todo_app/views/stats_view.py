"""Statistics view - Matplotlib charts summarizing productivity."""
from __future__ import annotations

from typing import Dict, Optional

import customtkinter as ctk
import matplotlib

# Use the TkAgg backend so charts embed inside a Tk window.
matplotlib.use("TkAgg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

from ..controllers.statistics_controller import StatisticsController
from ..utils.constants import PRIORITY_COLORS, STATUS_COLORS
from .theme import THEME
from .widgets import Card, SectionHeader, StatTile


class StatsView(ctk.CTkFrame):
    """Charts and headline numbers summarizing the user's productivity."""

    def __init__(
        self,
        master,
        stats_controller: StatisticsController,
        task_controller,
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.stats_controller = stats_controller
        self.task_controller = task_controller
        # Each chart card maps to one (figure, canvas, axes) tuple
        self._charts: Dict[str, tuple] = {}
        self._build()
        self.refresh()

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 4))
        SectionHeader(
            header, title="Statistics",
            subtitle="Insights into your productivity",
            icon="\U0001F4C8",
        ).pack(anchor="w")

        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.grid(row=1, column=0, sticky="ew", padx=24, pady=8)
        kpi_row.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="col")

        self.kpi_completion = StatTile(
            kpi_row, "Completion Rate", "0%", icon="\U0001F3AF", accent=THEME.color("success"),
        )
        self.kpi_completion.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.kpi_avg = StatTile(
            kpi_row, "Avg Tasks / Day", "0", icon="\U0001F4CA", accent=THEME.color("accent"),
        )
        self.kpi_avg.grid(row=0, column=1, sticky="ew", padx=6)
        self.kpi_streak = StatTile(
            kpi_row, "Streak", "0 days", icon="\U0001F525", accent=THEME.color("danger"),
        )
        self.kpi_streak.grid(row=0, column=2, sticky="ew", padx=6)
        self.kpi_productive = StatTile(
            kpi_row, "Most Productive", "—", icon="\U0001F3C6", accent=THEME.color("warning"),
        )
        self.kpi_productive.grid(row=0, column=3, sticky="ew", padx=(6, 0))

        # Chart grid
        charts = ctk.CTkFrame(self, fg_color="transparent")
        charts.grid(row=2, column=0, sticky="nsew", padx=24, pady=(8, 16))
        charts.grid_columnconfigure((0, 1), weight=1, uniform="col")
        charts.grid_rowconfigure((0, 1), weight=1, uniform="row")

        self.chart_week_card, self.chart_week_axes = self._build_chart_card(
            charts, "Completed This Week", 0, 0, "week"
        )
        self.chart_month_card, self.chart_month_axes = self._build_chart_card(
            charts, "Completed This Month", 0, 1, "month"
        )
        self.chart_category_card, self.chart_category_axes = self._build_chart_card(
            charts, "Category Distribution", 1, 0, "category"
        )
        self.chart_priority_card, self.chart_priority_axes = self._build_chart_card(
            charts, "Status & Priority", 1, 1, "priority"
        )

    def _build_chart_card(self, parent, title: str, row: int, col: int, key: str):
        """Create a card with a fixed matplotlib figure bound to a holder."""
        card = Card(parent)
        card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)
        SectionHeader(card, title=title).grid(row=0, column=0, sticky="ew",
                                              padx=18, pady=(16, 4))

        # Plain tk.Frame as matplotlib host - avoids the CTkFrame _canvas conflict
        import tkinter as tk
        holder = tk.Frame(card, bg=THEME.color("surface_alt"),
                           highlightthickness=0, bd=0)
        holder.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        holder.grid_columnconfigure(0, weight=1)
        holder.grid_rowconfigure(0, weight=1)

        fig = plt.Figure(figsize=(5, 3.2), dpi=100)
        fig.patch.set_facecolor(THEME.color("card"))
        ax = fig.add_subplot(111)
        ax.set_facecolor(THEME.color("card"))
        canvas = FigureCanvasTkAgg(fig, master=holder)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self._charts[key] = (fig, canvas, ax)
        return card, ax

    # ------------------------------------------------------------------
    def refresh(self) -> None:
        self._refresh_kpis()
        self._refresh_chart_week()
        self._refresh_chart_month()
        self._refresh_chart_category()
        self._refresh_chart_priority()

    def _refresh_kpis(self) -> None:
        completion = self.stats_controller.completion_rate()
        avg = self.stats_controller.average_tasks_per_day()
        streak = self.task_controller.streak()
        day, _ = self.stats_controller.most_productive_day()
        self.kpi_completion.set_value(f"{completion}%")
        self.kpi_avg.set_value(f"{avg}")
        self.kpi_streak.set_value(f"{streak['current']} days")
        self.kpi_productive.set_value(day)

    # ------------------------------------------------------------------
    def _style_axes(self, ax) -> None:
        ax.set_facecolor(THEME.color("card"))
        ax.tick_params(colors=THEME.color("text_muted"))
        for spine in ax.spines.values():
            spine.set_color(THEME.color("border"))
        ax.title.set_color(THEME.color("text"))
        ax.xaxis.label.set_color(THEME.color("text_muted"))
        ax.yaxis.label.set_color(THEME.color("text_muted"))

    def _refresh_chart_week(self) -> None:
        data = self.stats_controller.completed_last_week()
        import datetime as _dt
        dates = [_dt.date.fromisoformat(d) for d in data.keys()]
        values = list(data.values())
        fig, canvas, ax = self._charts["week"]
        ax.clear()
        ax.bar(dates, values, color=THEME.color("accent"),
               edgecolor=THEME.color("accent_hover"))
        ax.set_title("Tasks completed (last 7 days)",
                     color=THEME.color("text"), fontsize=12)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%a"))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(axis="y", color=THEME.color("border"), linestyle="--", alpha=0.4)
        self._style_axes(ax)
        fig.tight_layout()
        canvas.draw()

    def _refresh_chart_month(self) -> None:
        data = self.stats_controller.completed_last_month()
        import datetime as _dt
        dates = [_dt.date.fromisoformat(d) for d in data.keys()]
        values = list(data.values())
        fig, canvas, ax = self._charts["month"]
        ax.clear()
        ax.fill_between(dates, values, color=THEME.color("success"), alpha=0.3)
        ax.plot(dates, values, color=THEME.color("success"), linewidth=2)
        ax.set_title("Productivity (last 30 days)",
                     color=THEME.color("text"), fontsize=12)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        ax.grid(True, color=THEME.color("border"), linestyle="--", alpha=0.4)
        self._style_axes(ax)
        fig.tight_layout()
        canvas.draw()

    def _refresh_chart_category(self) -> None:
        data = self.stats_controller.category_distribution()
        if not data:
            data = {"No data": 1}
        fig, canvas, ax = self._charts["category"]
        ax.clear()
        labels = list(data.keys())
        values = list(data.values())
        colors = [
            THEME.color("accent"), THEME.color("success"), THEME.color("warning"),
            THEME.color("danger"), THEME.color("critical"),
        ] * (len(labels) // 5 + 1)
        colors = colors[: len(labels)]
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, colors=colors,
            autopct="%1.1f%%", startangle=90,
            textprops={"color": THEME.color("text")},
        )
        for at in autotexts:
            at.set_color("white")
            at.set_fontsize(9)
        ax.set_title("Tasks by category", color=THEME.color("text"), fontsize=12)
        fig.tight_layout()
        canvas.draw()

    def _refresh_chart_priority(self) -> None:
        statuses = self.stats_controller.status_distribution()
        priorities = self.stats_controller.priority_distribution()
        fig, canvas, ax = self._charts["priority"]
        ax.clear()
        # Two-bar layout in a single axes
        import numpy as np
        width = 0.35
        if statuses:
            s_keys = list(statuses.keys())
            s_vals = list(statuses.values())
            x1 = np.arange(len(s_keys))
            colors1 = [STATUS_COLORS.get(k, THEME.color("accent")) for k in s_keys]
            ax.bar(x1 - width / 2, s_vals, width, color=colors1, label="Status")
            for i, v in enumerate(s_vals):
                ax.text(x1[i] - width / 2, v + 0.05, str(v),
                        ha="center", color=THEME.color("text_muted"), fontsize=8)
        if priorities:
            p_keys = list(priorities.keys())
            p_vals = list(priorities.values())
            x2 = np.arange(len(p_keys))
            colors2 = [PRIORITY_COLORS.get(k, THEME.color("accent")) for k in p_keys]
            ax.bar(x2 + width / 2, p_vals, width, color=colors2, label="Priority")
            for i, v in enumerate(p_vals):
                ax.text(x2[i] + width / 2, v + 0.05, str(v),
                        ha="center", color=THEME.color("text_muted"), fontsize=8)
        if statuses or priorities:
            keys = (s_keys if statuses else []) + (p_keys if priorities else [])
            ax.set_xticks(range(len(keys)))
            ax.set_xticklabels(keys, rotation=20, ha="right",
                               color=THEME.color("text_muted"))
        ax.set_title("Status & Priority", color=THEME.color("text"), fontsize=12)
        ax.legend(facecolor=THEME.color("card"), edgecolor=THEME.color("border"),
                  labelcolor=THEME.color("text"))
        self._style_axes(ax)
        fig.tight_layout()
        canvas.draw()
