"""Entry point for Akena Todo - launches the desktop application."""
from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path


def _project_root() -> Path:
    """Return the directory that contains the ``todo_app`` package.

    Works both in development (``python main.py`` from project root) and
    when packaged with PyInstaller.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _setup_path() -> None:
    root = _project_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def main() -> int:
    _setup_path()
    root = _project_root()
    base_dir = root / "todo_app_data"
    base_dir.mkdir(exist_ok=True)

    # Configure logging first so we capture early errors.
    from todo_app.utils.logger import configure_logging, get_logger
    from todo_app.database.db_manager import init_db

    configure_logging(base_dir / "logs")
    log = get_logger("main")

    try:
        init_db(base_dir)
    except Exception:
        log.exception("Failed to initialize database")
        traceback.print_exc()
        return 1

    try:
        from todo_app.views.main_window import MainWindow
    except Exception:
        log.exception("Failed to import UI")
        traceback.print_exc()
        return 1

    try:
        app = MainWindow(base_dir)
        app.mainloop()
    except Exception:
        log.exception("Unhandled error in main loop")
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
