"""Subtask model - checklist items within a parent task."""
from __future__ import annotations

import datetime as _dt
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.db_manager import Base


class Subtask(Base):
    """A single checklist item belonging to a Task."""

    __tablename__ = "subtasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[_dt.datetime] = mapped_column(
        DateTime, default=_dt.datetime.utcnow, nullable=False
    )

    task = relationship("Task", back_populates="subtasks")

    def toggle(self) -> None:
        self.is_done = not self.is_done

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "is_done": self.is_done,
            "sort_index": self.sort_index,
        }

    def __repr__(self) -> str:
        status = "done" if self.is_done else "open"
        return f"<Subtask #{self.id} '{self.title}' [{status}]>"
