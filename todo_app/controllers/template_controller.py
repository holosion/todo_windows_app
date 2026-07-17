"""TemplateController - business logic for task templates."""
from __future__ import annotations

from typing import List, Optional

from ..database.db_manager import DatabaseManager
from ..models.template import TaskTemplate
from ..utils.logger import get_logger


class TemplateController:
    """All template-related operations live here."""

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db
        self.logger = get_logger("controller.template")

    def list_templates(self) -> List[TaskTemplate]:
        with self.db.session() as session:
            return session.query(TaskTemplate).order_by(TaskTemplate.name).all()

    def get_template(self, template_id: int) -> Optional[TaskTemplate]:
        with self.db.session() as session:
            return session.get(TaskTemplate, template_id)

    def create_template(
        self,
        name: str,
        title: str,
        description: str = "",
        notes: str = "",
        category: str = "Personal",
        priority: str = "Medium",
        estimated_duration: Optional[int] = None,
        repeat: str = "None",
        tags: str = "",
        color_tag: str = "#0EA5E9",
    ) -> TaskTemplate:
        with self.db.session() as session:
            tmpl = TaskTemplate(
                name=name.strip(),
                title=title.strip(),
                description=description,
                notes=notes,
                category=category,
                priority=priority,
                estimated_duration=estimated_duration,
                repeat=repeat,
                tags=tags,
                color_tag=color_tag,
            )
            session.add(tmpl)
            session.flush()
            session.refresh(tmpl)
            self.logger.info("Created template '%s'", name)
            return tmpl

    def update_template(self, template_id: int, **fields) -> Optional[TaskTemplate]:
        allowed = {
            "name", "title", "description", "notes", "category",
            "priority", "estimated_duration", "repeat", "tags", "color_tag",
        }
        with self.db.session() as session:
            tmpl = session.get(TaskTemplate, template_id)
            if tmpl is None:
                return None
            for key, value in fields.items():
                if key in allowed:
                    setattr(tmpl, key, value)
            return tmpl

    def delete_template(self, template_id: int) -> bool:
        with self.db.session() as session:
            tmpl = session.get(TaskTemplate, template_id)
            if tmpl is None:
                return False
            session.delete(tmpl)
            self.logger.info("Deleted template #%s", template_id)
            return True

    def get_template_data(self, template_id: int) -> Optional[dict]:
        """Return a dict suitable for passing to TaskController.create_task."""
        tmpl = self.get_template(template_id)
        if tmpl is None:
            return None
        return {
            "title": tmpl.title,
            "description": tmpl.description,
            "notes": tmpl.notes,
            "category": tmpl.category,
            "priority": tmpl.priority,
            "estimated_duration": tmpl.estimated_duration,
            "repeat": tmpl.repeat,
            "color_tag": tmpl.color_tag,
        }
