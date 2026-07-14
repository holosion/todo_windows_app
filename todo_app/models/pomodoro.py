"""Pomodoro session log - one row per work or break session."""
from __future__ import annotations

import datetime as _dt

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database.db_manager import Base


class PomodoroSession(Base):
    """A completed pomodoro / break / focus session."""

    __tablename__ = "pomodoro_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String(20), default="work", nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=25, nullable=False)
    started_at: Mapped[_dt.datetime] = mapped_column(
        DateTime, default=_dt.datetime.utcnow, nullable=False
    )
    ended_at: Mapped[_dt.datetime] = mapped_column(DateTime, nullable=True)
    completed: Mapped[bool] = mapped_column(Integer, default=1, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Pomodoro #{self.id} {self.kind} {self.duration_minutes}m>"
