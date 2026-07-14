"""Application controllers - the M in MVC.

Each controller exposes a small, task-focused API for one domain
object (tasks, categories, settings, statistics, backups) and
owns all reads / writes for that entity.
"""
from .task_controller import TaskController
from .category_controller import CategoryController
from .settings_controller import SettingsController
from .statistics_controller import StatisticsController
from .backup_controller import BackupController
from .activity_controller import ActivityController
from .notification_service import NotificationService

__all__ = [
    "TaskController",
    "CategoryController",
    "SettingsController",
    "StatisticsController",
    "BackupController",
    "ActivityController",
    "NotificationService",
]
