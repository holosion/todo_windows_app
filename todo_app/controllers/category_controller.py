"""CategoryController - manage user-defined categories."""
from __future__ import annotations

from typing import List, Optional

from ..database.db_manager import DatabaseManager
from ..models.category import Category
from ..utils.logger import get_logger


class CategoryController:
    """Encapsulates CRUD for categories."""

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db
        self.logger = get_logger("controller.category")

    def list_categories(self) -> List[Category]:
        with self.db.session() as session:
            return (
                session.query(Category)
                .order_by(Category.name.asc())
                .all()
            )

    def add_category(self, name: str, color: str = "#0EA5E9", icon: str = "•") -> Category:
        name = (name or "").strip()
        if not name:
            raise ValueError("Category name is required")
        with self.db.session() as session:
            existing = session.query(Category).filter(Category.name == name).first()
            if existing is not None:
                return existing
            cat = Category(name=name, color=color, icon=icon)
            session.add(cat)
            session.flush()
            session.refresh(cat)
            self.logger.info("Added category '%s'", name)
            return cat

    def rename_category(self, category_id: int, new_name: str) -> Optional[Category]:
        new_name = (new_name or "").strip()
        if not new_name:
            raise ValueError("Category name is required")
        with self.db.session() as session:
            cat = session.get(Category, category_id)
            if cat is None:
                return None
            cat.name = new_name
            return cat

    def set_color(self, category_id: int, color: str) -> Optional[Category]:
        with self.db.session() as session:
            cat = session.get(Category, category_id)
            if cat is None:
                return None
            cat.color = color
            return cat

    def delete_category(self, category_id: int) -> bool:
        with self.db.session() as session:
            cat = session.get(Category, category_id)
            if cat is None:
                return False
            session.delete(cat)
            self.logger.info("Deleted category #%s", category_id)
            return True
