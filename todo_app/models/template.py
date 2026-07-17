"""Task template model - reusable task blueprints."""
from __future__ import annotations

import datetime as _dt
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database.db_manager import Base


class TaskTemplate(Base):
    """A saved template that can be used to quickly create new tasks."""

    __tablename__ = "task_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    category: Mapped[str] = mapped_column(String(128), default="Personal", nullable=False)
    priority: Mapped[str] = mapped_column(String(16), default="Medium", nullable=False)
    estimated_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    repeat: Mapped[str] = mapped_column(String(16), default="None", nullable=False)
    tags: Mapped[str] = mapped_column(String(512), default="", nullable=False)
    color_tag: Mapped[str] = mapped_column(String(16), default="#0EA5E9", nullable=False)

    created_at: Mapped[_dt.datetime] = mapped_column(
        DateTime, default=_dt.datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "notes": self.notes,
            "category": self.category,
            "priority": self.priority,
            "estimated_duration": self.estimated_duration,
            "repeat": self.repeat,
            "tags": self.tags,
            "color_tag": self.color_tag,
        }

    def __repr__(self) -> str:
        return f"<TaskTemplate '{self.name}' -> '{self.title}'>"
