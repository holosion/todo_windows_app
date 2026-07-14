"""Database manager - SQLAlchemy engine, session factory, and bootstrap.

The application is fully offline; the database lives in a single SQLite file
inside the project directory and is created on first launch.
"""
from __future__ import annotations

import json
import os
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from ..utils.constants import DB_FILENAME, DEFAULT_CATEGORIES, SETTINGS_KEY
from ..utils.helpers import ensure_dir
from ..utils.logger import get_logger


class Base(DeclarativeBase):
    """Common declarative base for all ORM models."""


# ---------------------------------------------------------------------------
# Defaults exposed to the rest of the app
# ---------------------------------------------------------------------------
DEFAULT_SETTINGS: dict = {
    "theme": "Dark",
    "accent_color": "#0EA5E9",
    "username": "Akena",
    "default_category": "Personal",
    "default_reminder": 10,
    "default_priority": "Medium",
    "default_repeat": "None",
    "font_size": 13,
    "notifications_enabled": True,
    "sound_enabled": True,
    "confetti_enabled": True,
    "startup_view": "Dashboard",
    "minimize_to_tray": False,
    "pomodoro_work": 25,
    "pomodoro_short_break": 5,
    "pomodoro_long_break": 15,
    "pomodoro_cycles": 4,
}


class DatabaseManager:
    """Owns the SQLAlchemy engine and session factory."""

    def __init__(self, db_path: str | os.PathLike[str]) -> None:
        self.db_path = Path(db_path)
        ensure_dir(self.db_path.parent)

        self.logger = get_logger("db")
        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            echo=False,
            future=True,
            connect_args={"check_same_thread": False},
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )
        self._initialized = False

    # ------------------------------------------------------------------
    # Schema management
    # ------------------------------------------------------------------
    def create_all(self) -> None:
        """Create all tables and seed default data on first run."""
        from .. import models  # noqa: F401  (registers models with Base)

        Base.metadata.create_all(self.engine)
        self._seed_defaults()
        self._initialized = True
        self.logger.info("Database initialized at %s", self.db_path)

    def _seed_defaults(self) -> None:
        """Insert default categories and settings if not already present."""
        from ..models.category import Category
        from ..models.settings import AppSettings

        with self.session() as session:
            existing_categories = {c.name for c in session.query(Category).all()}
            for name in DEFAULT_CATEGORIES:
                if name not in existing_categories:
                    session.add(Category(name=name))

            settings_row = (
                session.query(AppSettings).filter(AppSettings.key == SETTINGS_KEY).first()
            )
            if settings_row is None:
                session.add(
                    AppSettings(key=SETTINGS_KEY, value=json.dumps(DEFAULT_SETTINGS))
                )

    # ------------------------------------------------------------------
    # Settings helpers
    # ------------------------------------------------------------------
    def load_settings(self) -> dict:
        """Load application settings, falling back to defaults."""
        from ..models.settings import AppSettings

        with self.session() as session:
            row = session.query(AppSettings).filter(AppSettings.key == SETTINGS_KEY).first()
            if row is None or not row.value:
                return dict(DEFAULT_SETTINGS)
            try:
                data = json.loads(row.value)
            except (TypeError, ValueError):
                return dict(DEFAULT_SETTINGS)
            merged = dict(DEFAULT_SETTINGS)
            merged.update(data)
            return merged

    def save_settings(self, settings: dict) -> None:
        """Persist application settings as JSON."""
        from ..models.settings import AppSettings

        with self.session() as session:
            row = session.query(AppSettings).filter(AppSettings.key == SETTINGS_KEY).first()
            if row is None:
                session.add(AppSettings(key=SETTINGS_KEY, value=json.dumps(settings)))
            else:
                row.value = json.dumps(settings)
            session.commit()

    # ------------------------------------------------------------------
    # Session helper
    # ------------------------------------------------------------------
    @contextmanager
    def session(self) -> Iterator[Session]:
        """Yield a SQLAlchemy session with automatic commit/rollback."""
        sess: Session = self.SessionLocal()
        try:
            yield sess
            sess.commit()
        except Exception:
            sess.rollback()
            raise
        finally:
            sess.close()

    # ------------------------------------------------------------------
    # Backup / restore helpers
    # ------------------------------------------------------------------
    def backup_to(self, destination: str | os.PathLike[str]) -> Path:
        """Copy the database file to ``destination`` and return the path."""
        dest = Path(destination)
        ensure_dir(dest.parent)
        shutil.copy2(self.db_path, dest)
        self.logger.info("Database backed up to %s", dest)
        return dest

    def restore_from(self, source: str | os.PathLike[str]) -> None:
        """Replace the live database with a copy from ``source``."""
        src = Path(source)
        if not src.exists():
            raise FileNotFoundError(f"Backup file not found: {src}")
        # Close engine connections before overwriting the file
        self.engine.dispose()
        shutil.copy2(src, self.db_path)
        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            echo=False,
            future=True,
            connect_args={"check_same_thread": False},
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )
        self.logger.info("Database restored from %s", src)


# ---------------------------------------------------------------------------
# Module-level singleton helpers
# ---------------------------------------------------------------------------
_DB: Optional[DatabaseManager] = None


def init_db(base_dir: str | os.PathLike[str]) -> DatabaseManager:
    """Create the singleton database manager inside ``base_dir``."""
    global _DB
    if _DB is None:
        _DB = DatabaseManager(Path(base_dir) / DB_FILENAME)
        _DB.create_all()
    return _DB


def get_db() -> DatabaseManager:
    """Return the singleton database manager. Raises if not initialized."""
    if _DB is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _DB
