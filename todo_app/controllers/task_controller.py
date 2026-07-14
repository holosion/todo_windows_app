"""TaskController - business logic for tasks.

Encapsulates every read / write that the UI needs to perform against the
Task model. The view layer never touches the database directly.
"""
from __future__ import annotations

import datetime as _dt
from typing import Iterable, List, Optional

from sqlalchemy import asc, desc, or_

from ..database.db_manager import DatabaseManager
from ..models.activity import ActivityLog
from ..models.category import Category
from ..models.task import Task
from ..utils.constants import PRIORITY_ORDER, PRIORITIES, STATUSES
from ..utils.helpers import combine_date_time
from ..utils.logger import get_logger


class TaskController:
    """All task-related operations live here."""

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db
        self.logger = get_logger("controller.task")

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    def create_task(
        self,
        title: str,
        description: str = "",
        category: Optional[str] = None,
        priority: str = "Medium",
        start_date: Optional[_dt.date] = None,
        due_date: Optional[_dt.date] = None,
        due_time: Optional[_dt.time] = None,
        estimated_duration: Optional[int] = None,
        notes: str = "",
        status: str = "Not Started",
        repeat: str = "None",
        reminder_minutes: int = 0,
        color_tag: str = "#0EA5E9",
        pinned: bool = False,
        favorite: bool = False,
        progress: int = 0,
    ) -> Task:
        """Create and persist a new task."""
        title = (title or "").strip()
        if not title:
            raise ValueError("Task title is required")
        if priority not in PRIORITIES:
            priority = "Medium"
        if status not in STATUSES:
            status = "Not Started"
        if progress < 0:
            progress = 0
        if progress > 100:
            progress = 100

        with self.db.session() as session:
            category_obj = self._resolve_category(session, category)
            max_index = (
                session.query(Task.sort_index).order_by(Task.sort_index.desc()).first()
            )
            next_index = (max_index[0] + 1) if max_index and max_index[0] is not None else 0

            task = Task(
                title=title,
                description=description,
                notes=notes,
                category=category_obj,
                priority=priority,
                start_date=start_date,
                due_date=due_date,
                due_time=due_time,
                estimated_duration=estimated_duration,
                status=status,
                progress=progress,
                repeat=repeat,
                reminder_minutes=reminder_minutes or 0,
                color_tag=color_tag,
                pinned=pinned,
                favorite=favorite,
                sort_index=next_index,
            )
            session.add(task)
            session.flush()
            self._log_activity(
                session,
                action="task_created",
                description=f"Created task '{task.title}'",
                icon="+",
            )
            session.refresh(task)
            self.logger.info("Created task #%s '%s'", task.id, task.title)
            return task

    def update_task(self, task_id: int, **fields) -> Optional[Task]:
        """Update one or more fields of a task. Returns the updated task or None."""
        allowed = {
            "title",
            "description",
            "notes",
            "category",
            "priority",
            "start_date",
            "due_date",
            "due_time",
            "estimated_duration",
            "status",
            "progress",
            "repeat",
            "reminder_minutes",
            "color_tag",
            "pinned",
            "favorite",
            "attachments",
        }
        with self.db.session() as session:
            task = session.get(Task, task_id)
            if task is None:
                return None
            for key, value in fields.items():
                if key not in allowed:
                    continue
                if key == "category":
                    task.category = self._resolve_category(session, value)
                else:
                    setattr(task, key, value)
            task.updated_at = _dt.datetime.utcnow()
            if task.status == "Completed" and not task.completed_at:
                task.completed_at = _dt.datetime.utcnow()
            if task.status != "Completed":
                task.completed_at = None
            self._log_activity(
                session,
                action="task_updated",
                description=f"Updated task '{task.title}'",
                icon="✎",
            )
            self.logger.info("Updated task #%s", task_id)
            return task

    def delete_task(self, task_id: int) -> bool:
        """Permanently delete a task. Returns True if a row was removed."""
        with self.db.session() as session:
            task = session.get(Task, task_id)
            if task is None:
                return False
            title = task.title
            session.delete(task)
            self._log_activity(
                session,
                action="task_deleted",
                description=f"Deleted task '{title}'",
                icon="🗑",
            )
            self.logger.info("Deleted task #%s", task_id)
            return True

    def get_task(self, task_id: int) -> Optional[Task]:
        with self.db.session() as session:
            return session.get(Task, task_id)

    def list_tasks(
        self,
        include_archived: bool = False,
        include_completed: bool = True,
    ) -> List[Task]:
        with self.db.session() as session:
            query = session.query(Task)
            if not include_archived:
                query = query.filter(Task.archived.is_(False))
            if not include_completed:
                query = query.filter(Task.status != "Completed")
            return query.order_by(Task.sort_index.asc(), Task.id.asc()).all()

    # ------------------------------------------------------------------
    # Workflow shortcuts
    # ------------------------------------------------------------------
    def mark_completed(self, task_id: int) -> Optional[Task]:
        with self.db.session() as session:
            task = session.get(Task, task_id)
            if task is None:
                return None
            task.mark_completed()
            task.reminder_sent = True
            self._log_activity(
                session,
                action="task_completed",
                description=f"Completed task '{task.title}'",
                icon="✓",
            )
            return task

    def mark_in_progress(self, task_id: int) -> Optional[Task]:
        return self.update_task(task_id, status="In Progress")

    def duplicate_task(self, task_id: int) -> Optional[Task]:
        with self.db.session() as session:
            src = session.get(Task, task_id)
            if src is None:
                return None
            new_task = Task(
                title=f"{src.title} (Copy)",
                description=src.description,
                notes=src.notes,
                category=src.category,
                priority=src.priority,
                start_date=src.start_date,
                due_date=src.due_date,
                due_time=src.due_time,
                estimated_duration=src.estimated_duration,
                status="Not Started",
                progress=0,
                repeat=src.repeat,
                reminder_minutes=src.reminder_minutes,
                color_tag=src.color_tag,
                pinned=False,
                favorite=False,
                sort_index=src.sort_index + 1,
                attachments=src.attachments,
            )
            session.add(new_task)
            session.flush()
            self._log_activity(
                session,
                action="task_duplicated",
                description=f"Duplicated task '{src.title}'",
                icon="⎘",
            )
            session.refresh(new_task)
            return new_task

    def archive_task(self, task_id: int, archived: bool = True) -> Optional[Task]:
        with self.db.session() as session:
            task = session.get(Task, task_id)
            if task is None:
                return None
            task.archived = archived
            self._log_activity(
                session,
                action="task_archived" if archived else "task_restored",
                description=(
                    f"Archived task '{task.title}'"
                    if archived
                    else f"Restored task '{task.title}'"
                ),
                icon="📦" if archived else "↩",
            )
            return task

    def restore_task(self, task_id: int) -> Optional[Task]:
        return self.archive_task(task_id, False)

    def toggle_pin(self, task_id: int) -> Optional[Task]:
        with self.db.session() as session:
            task = session.get(Task, task_id)
            if task is None:
                return None
            task.pinned = not task.pinned
            return task

    def toggle_favorite(self, task_id: int) -> Optional[Task]:
        with self.db.session() as session:
            task = session.get(Task, task_id)
            if task is None:
                return None
            task.favorite = not task.favorite
            return task

    def set_progress(self, task_id: int, progress: int) -> Optional[Task]:
        progress = max(0, min(100, int(progress)))
        status = "Not Started" if progress == 0 else "In Progress"
        if progress == 100:
            return self.mark_completed(task_id)
        return self.update_task(task_id, progress=progress, status=status)

    def reorder(self, ordered_ids: Iterable[int]) -> None:
        """Persist a new display order for the given task ids."""
        with self.db.session() as session:
            for index, task_id in enumerate(ordered_ids):
                task = session.get(Task, task_id)
                if task is not None:
                    task.sort_index = index

    # ------------------------------------------------------------------
    # Search / filter / sort
    # ------------------------------------------------------------------
    def search(
        self,
        query: str = "",
        *,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        start: Optional[_dt.date] = None,
        end: Optional[_dt.date] = None,
        archived: bool = False,
    ) -> List[Task]:
        with self.db.session() as session:
            q = session.query(Task).filter(Task.archived.is_(archived))
            if query:
                pattern = f"%{query.lower()}%"
                q = q.filter(
                    or_(
                        Task.title.ilike(pattern),
                        Task.description.ilike(pattern),
                        Task.notes.ilike(pattern),
                    )
                )
            if category:
                q = q.join(Category).filter(Category.name == category)
            if priority:
                q = q.filter(Task.priority == priority)
            if status:
                q = q.filter(Task.status == status)
            if start:
                q = q.filter(Task.due_date >= start)
            if end:
                q = q.filter(Task.due_date <= end)
            return q.order_by(Task.sort_index.asc()).all()

    def filter_preset(self, preset: str) -> List[Task]:
        """Return tasks matching a named filter preset."""
        today = _dt.date.today()
        if preset == "today":
            return self.search(start=today, end=today)
        if preset == "tomorrow":
            tomorrow = today + _dt.timedelta(days=1)
            return self.search(start=tomorrow, end=tomorrow)
        if preset == "this_week":
            start = today - _dt.timedelta(days=today.weekday())
            end = start + _dt.timedelta(days=6)
            return self.search(start=start, end=end)
        if preset == "this_month":
            start = today.replace(day=1)
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1) - _dt.timedelta(days=1)
            else:
                end = start.replace(month=start.month + 1) - _dt.timedelta(days=1)
            return self.search(start=start, end=end)
        if preset == "completed":
            return self.search(status="Completed")
        if preset == "incomplete":
            with self.db.session() as session:
                return (
                    session.query(Task)
                    .filter(Task.archived.is_(False))
                    .filter(Task.status != "Completed")
                    .order_by(Task.sort_index.asc())
                    .all()
                )
        if preset == "high_priority":
            return self.search(priority="High")
        if preset == "overdue":
            with self.db.session() as session:
                tasks = (
                    session.query(Task)
                    .filter(Task.archived.is_(False))
                    .filter(Task.status.notin_(["Completed", "Cancelled"]))
                    .all()
                )
                return [t for t in tasks if t.is_overdue()]
        if preset == "archived":
            with self.db.session() as session:
                return (
                    session.query(Task)
                    .filter(Task.archived.is_(True))
                    .order_by(Task.updated_at.desc())
                    .all()
                )
        if preset == "pinned":
            with self.db.session() as session:
                return (
                    session.query(Task)
                    .filter(Task.archived.is_(False))
                    .filter(Task.pinned.is_(True))
                    .order_by(Task.sort_index.asc())
                    .all()
                )
        if preset == "favorites":
            with self.db.session() as session:
                return (
                    session.query(Task)
                    .filter(Task.archived.is_(False))
                    .filter(Task.favorite.is_(True))
                    .order_by(Task.sort_index.asc())
                    .all()
                )
        return self.list_tasks()

    def sort(self, tasks: List[Task], key: str, descending: bool = False) -> List[Task]:
        """Return a sorted copy of ``tasks``."""
        if key == "priority":
            ordered = sorted(tasks, key=lambda t: PRIORITY_ORDER.get(t.priority, 99))
        elif key == "due_date":
            ordered = sorted(tasks, key=lambda t: t.due_date or _dt.date.max)
        elif key == "title":
            ordered = sorted(tasks, key=lambda t: t.title.lower())
        elif key == "status":
            ordered = sorted(tasks, key=lambda t: t.status)
        elif key == "created_at":
            ordered = sorted(tasks, key=lambda t: t.created_at)
        else:
            ordered = list(tasks)
        if descending:
            ordered.reverse()
        return ordered

    # ------------------------------------------------------------------
    # Dashboard helpers
    # ------------------------------------------------------------------
    def today_progress(self) -> dict:
        """Return counts needed by the dashboard."""
        today = _dt.date.today()
        with self.db.session() as session:
            tasks = (
                session.query(Task)
                .filter(Task.archived.is_(False))
                .all()
            )
        today_tasks = [t for t in tasks if t.due_date == today]
        completed = sum(1 for t in today_tasks if t.status == "Completed")
        total = len(today_tasks)
        remaining = max(0, total - completed)
        pct = int(round((completed / total) * 100)) if total else 0
        return {
            "completed": completed,
            "remaining": remaining,
            "total": total,
            "percent": pct,
        }

    def upcoming_deadlines(self, limit: int = 5) -> List[Task]:
        today = _dt.date.today()
        now = _dt.datetime.now()
        with self.db.session() as session:
            tasks = (
                session.query(Task)
                .filter(Task.archived.is_(False))
                .filter(Task.due_date.isnot(None))
                .filter(Task.status.notin_(["Completed", "Cancelled"]))
                .order_by(Task.due_date.asc(), Task.due_time.asc())
                .all()
            )
        upcoming: List[Task] = []
        for task in tasks:
            if task.due_date and task.due_date >= today:
                upcoming.append(task)
            elif task.due_date == today and combine_date_time(
                task.due_date, task.due_time
            ) and combine_date_time(task.due_date, task.due_time) > now:
                upcoming.append(task)
        return upcoming[:limit]

    def streak(self) -> dict:
        """Compute current / longest streak of days with completed tasks."""
        with self.db.session() as session:
            completed = (
                session.query(Task)
                .filter(Task.status == "Completed")
                .filter(Task.completed_at.isnot(None))
                .all()
            )
        days = {
            (t.completed_at + _dt.timedelta(hours=3)).date()  # EAT offset for stability
            for t in completed
        }
        if not days:
            return {"current": 0, "longest": 0, "days_completed": 0}

        sorted_days = sorted(days)
        longest = 1
        run = 1
        for prev, curr in zip(sorted_days, sorted_days[1:]):
            if (curr - prev).days == 1:
                run += 1
                longest = max(longest, run)
            else:
                run = 1

        today = _dt.date.today()
        current = 0
        cursor = today
        while cursor in days:
            current += 1
            cursor -= _dt.timedelta(days=1)

        return {
            "current": current,
            "longest": longest,
            "days_completed": len(days),
        }

    def weekly_progress(self) -> dict:
        today = _dt.date.today()
        start = today - _dt.timedelta(days=today.weekday())
        end = start + _dt.timedelta(days=6)
        with self.db.session() as session:
            tasks = (
                session.query(Task)
                .filter(Task.archived.is_(False))
                .filter(Task.due_date >= start)
                .filter(Task.due_date <= end)
                .all()
            )
        completed = sum(1 for t in tasks if t.status == "Completed")
        total = len(tasks)
        pct = int(round((completed / total) * 100)) if total else 0
        return {
            "completed": completed,
            "total": total,
            "percent": pct,
            "start": start,
            "end": end,
        }

    def monthly_progress(self) -> dict:
        today = _dt.date.today()
        start = today.replace(day=1)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1) - _dt.timedelta(days=1)
        else:
            end = start.replace(month=start.month + 1) - _dt.timedelta(days=1)
        with self.db.session() as session:
            tasks = (
                session.query(Task)
                .filter(Task.archived.is_(False))
                .filter(Task.due_date >= start)
                .filter(Task.due_date <= end)
                .all()
            )
        completed = sum(1 for t in tasks if t.status == "Completed")
        total = len(tasks)
        pct = int(round((completed / total) * 100)) if total else 0
        return {
            "completed": completed,
            "total": total,
            "percent": pct,
            "start": start,
            "end": end,
        }

    def daily_goals(self) -> dict:
        """Return the current daily goal vs. completed tasks today."""
        settings = self.db.load_settings()
        goal = int(settings.get("daily_goal", 5))
        progress = self.today_progress()
        return {
            "goal": goal,
            "completed": progress["completed"],
            "percent": min(100, int(progress["completed"] * 100 / goal)) if goal else 0,
        }

    def weekly_goals(self) -> dict:
        settings = self.db.load_settings()
        goal = int(settings.get("weekly_goal", 25))
        progress = self.weekly_progress()
        return {
            "goal": goal,
            "completed": progress["completed"],
            "percent": min(100, int(progress["completed"] * 100 / goal)) if goal else 0,
        }

    def monthly_goals(self) -> dict:
        settings = self.db.load_settings()
        goal = int(settings.get("monthly_goal", 100))
        progress = self.monthly_progress()
        return {
            "goal": goal,
            "completed": progress["completed"],
            "percent": min(100, int(progress["completed"] * 100 / goal)) if goal else 0,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _resolve_category(self, session, name: Optional[str]) -> Optional[Category]:
        if not name:
            return None
        category = session.query(Category).filter(Category.name == name).first()
        if category is not None:
            return category
        category = Category(name=name)
        session.add(category)
        session.flush()
        return category

    def _log_activity(
        self, session, action: str, description: str, icon: str = "•"
    ) -> None:
        session.add(
            ActivityLog(action=action, description=description, icon=icon)
        )
