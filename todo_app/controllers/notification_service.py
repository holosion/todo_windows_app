"""NotificationService - periodically checks for due reminders and fires them."""
from __future__ import annotations

import datetime as _dt
from typing import Callable, Optional

from ..controllers.task_controller import TaskController
from ..models.notification import Notification
from ..models.task import Task
from ..utils.helpers import combine_date_time
from ..utils.logger import get_logger


class NotificationService:
    """Polls the database for due reminders and dispatches system notifications."""

    POLL_MS = 30_000

    def __init__(
        self,
        task_controller: TaskController,
        on_fire: Optional[Callable[[str, str], None]] = None,
    ) -> None:
        self.task_controller = task_controller
        self.on_fire = on_fire
        self._id: Optional[str] = None
        self._running = False
        self.logger = get_logger("notifier")
        self._last_signature: set[tuple[int, str]] = set()

    def start(self, root) -> None:
        if self._running:
            return
        self._running = True
        self._root = root
        self._schedule()

    def stop(self) -> None:
        self._running = False
        if self._id is not None:
            try:
                self._root.after_cancel(self._id)
            except Exception:
                pass
            self._id = None

    def _schedule(self) -> None:
        if not self._running:
            return
        self.tick()
        self._id = self._root.after(self.POLL_MS, self._schedule)

    def tick(self) -> None:
        """Inspect reminders and fire any that are due."""
        try:
            self._check_due_tasks()
        except Exception as exc:  # noqa: BLE001
            self.logger.exception("Notifier tick failed: %s", exc)

    def _check_due_tasks(self) -> None:
        now = _dt.datetime.now()
        with self.task_controller.db.session() as session:
            tasks = (
                session.query(Task)
                .filter(Task.archived.is_(False))
                .filter(Task.status != "Completed")
                .filter(Task.due_date.isnot(None))
                .all()
            )
            for t in tasks:
                fire_at = self._fire_time(t, now)
                if fire_at is None:
                    continue
                if fire_at <= now and not t.reminder_sent:
                    self._fire(t, fire_at)
                    t.reminder_sent = True
                    session.add(
                        Notification(
                            task_id=t.id,
                            title=f"Reminder: {t.title}",
                            message=t.description or "Task is due",
                            fire_at=fire_at,
                            delivered=True,
                            delivered_at=now,
                        )
                    )

    def _fire_time(self, task: Task, now: _dt.datetime) -> Optional[_dt.datetime]:
        if task.due_date is None:
            return None
        due = combine_date_time(task.due_date, task.due_time)
        if due is None:
            return None
        if task.reminder_minutes and task.reminder_minutes > 0:
            return due - _dt.timedelta(minutes=task.reminder_minutes)
        # If no reminder configured, still alert when overdue by 5 min
        if due < now and (now - due) < _dt.timedelta(minutes=10):
            return now
        return None

    def _fire(self, task: Task, fire_at: _dt.datetime) -> None:
        message = f"Due {task.due_date.isoformat()}"
        if task.due_time:
            message += f" at {task.due_time.strftime('%H:%M')}"
        if task.category:
            message += f"  •  {task.category.name}"
        self.logger.info("Firing reminder for task #%s", task.id)
        if self.on_fire is not None:
            try:
                self.on_fire(task.title, message)
            except Exception as exc:  # noqa: BLE001
                self.logger.warning("Local notifier callback failed: %s", exc)
        self._system_notify(task.title, message)

    @staticmethod
    def _system_notify(title: str, message: str) -> None:
        try:
            from plyer import notification
            notification.notify(
                title=title, message=message, app_name="Akena Todo", timeout=8
            )
        except Exception:
            # Fall back to a Tk bell - no network required.
            try:
                import tkinter as tk
                tk.Tk.bell()
            except Exception:
                pass
