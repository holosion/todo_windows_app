"""Category model - user-defined grouping for tasks."""
from __future__ import annotations

from typing import List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.db_manager import Base


class Category(Base):
    """A user-defined category such as 'University' or 'Coding'."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(16), default="#0EA5E9", nullable=False)
    icon: Mapped[str] = mapped_column(String(16), default="•", nullable=False)

    tasks: Mapped[List["Task"]] = relationship(  # type: ignore[name-defined]
        "Task", back_populates="category", cascade="save-update"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Category #{self.id} {self.name!r}>"
