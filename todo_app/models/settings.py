"""Key/value application settings stored in the database."""
from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database.db_manager import Base


class AppSettings(Base):
    """A single-row-per-key configuration table.

    Values are stored as JSON-encoded strings so complex settings
    (lists, dicts) round-trip cleanly.
    """

    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, default="", nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AppSettings {self.key}={self.value[:32]!r}>"
