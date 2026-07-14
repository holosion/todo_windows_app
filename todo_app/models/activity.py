"""Activity log - records user-visible actions for the 'Recent activity' feature."""
from __future__ import annotations

import datetime as _dt

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database.db_manager import Base


class ActivityLog(Base):
    """A single activity entry shown in the dashboard's 'Recent activity' widget."""

    __tablename__ = "activity_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    icon: Mapped[str] = mapped_column(String(8), default="•", nullable=False)
    created_at: Mapped[_dt.datetime] = mapped_column(
        DateTime, default=_dt.datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ActivityLog #{self.id} {self.action}>"
