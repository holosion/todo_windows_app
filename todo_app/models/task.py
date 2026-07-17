"""Task model - the central entity of the application."""
from __future__ import annotations

import datetime as _dt
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.db_manager import Base


class Task(Base):
    """Represents a single task / to-do item."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)

    # ------------------------------------------------------------------
    # Categorization
    # ------------------------------------------------------------------
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    category = relationship("Category", back_populates="tasks", lazy="joined")

    priority: Mapped[str] = mapped_column(String(16), default="Medium", nullable=False)
    color_tag: Mapped[str] = mapped_column(String(16), default="#0EA5E9", nullable=False)

    # ------------------------------------------------------------------
    # Scheduling
    # ------------------------------------------------------------------
    start_date: Mapped[Optional[_dt.date]] = mapped_column(Date, nullable=True)
    due_date: Mapped[Optional[_dt.date]] = mapped_column(Date, nullable=True)
    due_time: Mapped[Optional[_dt.time]] = mapped_column(Time, nullable=True)
    estimated_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------
    status: Mapped[str] = mapped_column(String(20), default="Not Started", nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    repeat: Mapped[str] = mapped_column(String(16), default="None", nullable=False)
    reminder_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------
    created_at: Mapped[_dt.datetime] = mapped_column(
        DateTime, default=_dt.datetime.utcnow, nullable=False
    )
    updated_at: Mapped[_dt.datetime] = mapped_column(
        DateTime,
        default=_dt.datetime.utcnow,
        onupdate=_dt.datetime.utcnow,
        nullable=False,
    )
    completed_at: Mapped[Optional[_dt.datetime]] = mapped_column(DateTime, nullable=True)

    # ------------------------------------------------------------------
    # Attachments
    # ------------------------------------------------------------------
    attachments: Mapped[str] = mapped_column(Text, default="", nullable=False)

    # ------------------------------------------------------------------
    # Tags (comma-separated string, e.g. "urgent,backend,api")
    # ------------------------------------------------------------------
    tags: Mapped[str] = mapped_column(String(512), default="", nullable=False)

    # ------------------------------------------------------------------
    # Ordering - used for drag-and-drop reordering
    # ------------------------------------------------------------------
    sort_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ------------------------------------------------------------------
    # Subtasks (one-to-many)
    # ------------------------------------------------------------------
    subtasks = relationship("Subtask", back_populates="task",
                            cascade="all, delete-orphan", lazy="selectin")

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------
    def is_completed(self) -> bool:
        """Return True when the task is in a completed state."""
        return self.status == "Completed"

    def is_overdue(self, now: Optional[_dt.datetime] = None) -> bool:
        """Return True when the task is past its due date/time and not completed."""
        if self.is_completed() or self.status == "Cancelled" or self.due_date is None:
            return False
        moment = now or _dt.datetime.now()
        due = _dt.datetime.combine(self.due_date, self.due_time or _dt.time(23, 59))
        return moment > due

    def mark_completed(self) -> None:
        """Mark this task as completed and stamp completion time."""
        self.status = "Completed"
        self.progress = 100
        self.completed_at = _dt.datetime.utcnow()

    def to_dict(self) -> dict:
        """Serialize the task into a JSON-friendly dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "notes": self.notes,
            "category": self.category.name if self.category else None,
            "priority": self.priority,
            "color_tag": self.color_tag,
            "tags": self.tags,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "due_time": self.due_time.isoformat() if self.due_time else None,
            "estimated_duration": self.estimated_duration,
            "status": self.status,
            "progress": self.progress,
            "repeat": self.repeat,
            "reminder_minutes": self.reminder_minutes,
            "pinned": self.pinned,
            "favorite": self.favorite,
            "archived": self.archived,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "attachments": self.attachments,
            "subtasks": [s.to_dict() for s in self.subtasks] if self.subtasks else [],
        }

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Task #{self.id} '{self.title}' status={self.status}>"
