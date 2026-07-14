"""ActivityController - persist and read the recent activity feed."""
from __future__ import annotations

from typing import List

from ..database.db_manager import DatabaseManager
from ..models.activity import ActivityLog


class ActivityController:
    """Reads / writes the dashboard's 'Recent activity' feed."""

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def recent(self, limit: int = 10) -> List[ActivityLog]:
        with self.db.session() as session:
            return (
                session.query(ActivityLog)
                .order_by(ActivityLog.created_at.desc())
                .limit(limit)
                .all()
            )

    def log(self, action: str, description: str, icon: str = "•") -> None:
        with self.db.session() as session:
            session.add(ActivityLog(action=action, description=description, icon=icon))
