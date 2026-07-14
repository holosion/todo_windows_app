"""BackupController - manage database backups and exports."""
from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List

from ..database.db_manager import DatabaseManager
from ..models.backup import Backup
from ..utils.helpers import ensure_dir, safe_filename
from ..utils.logger import get_logger


class BackupController:
    """Create, list, restore, and delete database backups."""

    def __init__(self, db: DatabaseManager, backup_dir: str | os.PathLike[str]) -> None:
        self.db = db
        self.backup_dir = Path(backup_dir)
        ensure_dir(self.backup_dir)
        self.logger = get_logger("controller.backup")

    def create_backup(self, note: str = "") -> Backup:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"akena_todo_backup_{stamp}.db"
        destination = self.backup_dir / filename
        self.db.backup_to(destination)

        with self.db.session() as session:
            entry = Backup(
                name=filename,
                path=str(destination),
                size_bytes=destination.stat().st_size,
                note=note,
            )
            session.add(entry)
            session.flush()
            session.refresh(entry)
            self.logger.info("Created backup %s", filename)
            return entry

    def list_backups(self) -> List[Backup]:
        with self.db.session() as session:
            return (
                session.query(Backup)
                .order_by(Backup.created_at.desc())
                .all()
            )

    def delete_backup(self, backup_id: int) -> bool:
        with self.db.session() as session:
            entry = session.get(Backup, backup_id)
            if entry is None:
                return False
            try:
                if os.path.exists(entry.path):
                    os.remove(entry.path)
            except OSError as exc:
                self.logger.warning("Could not remove backup file %s: %s", entry.path, exc)
            session.delete(entry)
            return True

    def restore_backup(self, backup_id: int) -> bool:
        with self.db.session() as session:
            entry = session.get(Backup, backup_id)
            if entry is None:
                return False
            path = entry.path
        if not os.path.exists(path):
            self.logger.error("Backup file missing: %s", path)
            return False
        self.db.restore_from(path)
        self.logger.info("Restored backup #%s", backup_id)
        return True

    def export_database(self, destination: str | os.PathLike[str]) -> Path:
        dest = Path(destination)
        ensure_dir(dest.parent)
        return self.db.backup_to(dest)

    def import_database(self, source: str | os.PathLike[str]) -> None:
        self.db.restore_from(source)
        self.logger.info("Imported database from %s", source)
