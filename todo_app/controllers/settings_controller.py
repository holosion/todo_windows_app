"""SettingsController - persist application preferences."""
from __future__ import annotations

import copy
from typing import Any

from ..database.db_manager import DEFAULT_SETTINGS, DatabaseManager
from ..utils.logger import get_logger


class SettingsController:
    """Reads / writes application settings through the database manager."""

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db
        self.logger = get_logger("controller.settings")
        self._cache: dict[str, Any] | None = None

    def get_all(self) -> dict:
        """Return all settings, falling back to defaults."""
        if self._cache is None:
            self._cache = self.db.load_settings()
        return copy.deepcopy(self._cache)

    def get(self, key: str, default: Any = None) -> Any:
        return self.get_all().get(key, default)

    def set(self, key: str, value: Any) -> None:
        data = self.get_all()
        data[key] = value
        self.db.save_settings(data)
        self._cache = data
        self.logger.debug("Setting %s=%s", key, value)

    def update(self, values: dict) -> None:
        data = self.get_all()
        data.update(values)
        self.db.save_settings(data)
        self._cache = data

    def reset(self) -> None:
        self.db.save_settings(dict(DEFAULT_SETTINGS))
        self._cache = dict(DEFAULT_SETTINGS)
