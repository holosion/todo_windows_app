"""StatisticsController - aggregate task data for charts and dashboards."""
from __future__ import annotations

import datetime as _dt
from collections import Counter
from typing import Dict, List, Tuple

from ..database.db_manager import DatabaseManager
from ..models.category import Category
from ..models.task import Task
from ..utils.helpers import combine_date_time


class StatisticsController:
    """Read-only aggregations for charts and dashboard widgets."""

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Time-based aggregations
    # ------------------------------------------------------------------
    def completed_last_week(self) -> Dict[str, int]:
        """Return {date_iso: count} of tasks completed in the last 7 days."""
        today = _dt.date.today()
        start = today - _dt.timedelta(days=6)
        with self.db.session() as session:
            tasks = (
                session.query(Task)
                .filter(Task.status == "Completed")
                .filter(Task.completed_at.isnot(None))
                .all()
            )
        buckets = {start + _dt.timedelta(days=i): 0 for i in range(7)}
        for t in tasks:
            if t.completed_at is None:
                continue
            day = (t.completed_at + _dt.timedelta(hours=3)).date()
            if day in buckets:
                buckets[day] += 1
        return {d.isoformat(): c for d, c in buckets.items()}

    def completed_last_month(self) -> Dict[str, int]:
        today = _dt.date.today()
        start = today - _dt.timedelta(days=29)
        with self.db.session() as session:
            tasks = (
                session.query(Task)
                .filter(Task.status == "Completed")
                .filter(Task.completed_at.isnot(None))
                .all()
            )
        buckets = {start + _dt.timedelta(days=i): 0 for i in range(30)}
        for t in tasks:
            if t.completed_at is None:
                continue
            day = (t.completed_at + _dt.timedelta(hours=3)).date()
            if day in buckets:
                buckets[day] += 1
        return {d.isoformat(): c for d, c in buckets.items()}

    def category_distribution(self) -> Dict[str, int]:
        with self.db.session() as session:
            tasks = session.query(Task).all()
        counter: Counter[str] = Counter()
        for t in tasks:
            key = t.category.name if t.category else "Uncategorized"
            counter[key] += 1
        return dict(counter)

    def productivity_over_time(self, days: int = 30) -> Dict[str, int]:
        return {
            "week": self.completed_last_week(),
            "month": self.completed_last_month(),
        }

    def completion_rate(self) -> float:
        with self.db.session() as session:
            tasks = session.query(Task).filter(Task.archived.is_(False)).all()
        if not tasks:
            return 0.0
        completed = sum(1 for t in tasks if t.status == "Completed")
        return round(completed * 100.0 / len(tasks), 1)

    def average_tasks_per_day(self, days: int = 30) -> float:
        with self.db.session() as session:
            cutoff = _dt.datetime.utcnow() - _dt.timedelta(days=days)
            tasks = (
                session.query(Task)
                .filter(Task.completed_at.isnot(None))
                .filter(Task.completed_at >= cutoff)
                .all()
            )
        if not tasks:
            return 0.0
        return round(len(tasks) / days, 2)

    def most_productive_day(self) -> Tuple[str, int]:
        with self.db.session() as session:
            tasks = (
                session.query(Task)
                .filter(Task.status == "Completed")
                .filter(Task.completed_at.isnot(None))
                .all()
            )
        if not tasks:
            return ("—", 0)
        counter: Counter[str] = Counter()
        for t in tasks:
            if t.completed_at is None:
                continue
            day = (t.completed_at + _dt.timedelta(hours=3)).date()
            counter[day.strftime("%A")] += 1
        day, count = counter.most_common(1)[0]
        return day, count

    def priority_distribution(self) -> Dict[str, int]:
        with self.db.session() as session:
            tasks = (
                session.query(Task)
                .filter(Task.archived.is_(False))
                .all()
            )
        return dict(Counter(t.priority for t in tasks))

    def status_distribution(self) -> Dict[str, int]:
        with self.db.session() as session:
            tasks = (
                session.query(Task)
                .filter(Task.archived.is_(False))
                .all()
            )
        return dict(Counter(t.status for t in tasks))
