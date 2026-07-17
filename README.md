# Akena Todo

A modern, fully offline desktop To-Do application for Windows. Plan, organize, and
track everything you do each day with a clean CustomTkinter UI, local SQLite
storage, charts, a Pomodoro timer, and confetti when you finish a tough day.

Inspired by Microsoft To Do, TickTick, and Notion's task manager — but 100%
offline, lightweight, and free.

---

## ✨ Features

### Dashboard
- Personalized greeting (Good Morning / Afternoon / Evening)
- Live clock and today's date
- Completed / Remaining / Progress %
- Current streak (🔥 days)
- Daily / Weekly / Monthly progress rings & bars
- Today's motivation quote
- Upcoming deadlines
- Recent activity log

### Task Management
- Create, edit, delete, duplicate, archive, restore
- Pinned & favorite tasks
- Color tags
- 5 statuses (Not Started / In Progress / Completed / Cancelled / Overdue)
- 4 priorities (Low / Medium / High / Critical) with distinct colors
- Repeat (None / Daily / Weekly / Monthly / Yearly)
- Reminders (5 min, 10 min, 30 min, 1 h, 1 day before due)
- Estimated duration
- Drag-and-drop reordering
- Instant search across title, description, notes
- 12 ready-made filter presets + 6 sort orders
- Custom categories (14 seeded by default)

### Views
- **Daily Planner** — 24-hour vertical timeline of your day
- **Calendar** — month grid, click a day to see its tasks
- **Statistics** — 4 charts (last 7 days, last 30 days, category distribution, status & priority) plus KPIs
- **Productivity** — Pomodoro timer, stopwatch, countdown, and daily / weekly / monthly goal tracking
- **Settings** — theme, accent color, font size, defaults, notifications, Pomodoro, backup & restore

### System
- **Light & Dark** themes with live switching
- **Offline-only** — no network, no telemetry
- **Local SQLite** — your data never leaves the machine
- **Auto-save** on every change
- **Backup & restore** — manual backups, export / import the database
- **Keyboard shortcuts**
  - `Ctrl+N` — New (quick add) task
  - `Ctrl+S` — Save (UX cue; saves are automatic)
  - `Ctrl+F` — Focus the search bar
  - `Ctrl+D` — Duplicate the selected task
  - `Ctrl+T` — Toggle theme
  - `Delete` — Delete the selected task
  - `Space` — Toggle complete on the selected task
- **Confetti** when every task for today is done 🎉
- **Task completion sound** (configurable in Settings)
- **Plyer-based reminders** + system bell fallback

---

## 🧰 Tech Stack

- **Python 3.10+** (tested on 3.13)
- **CustomTkinter** — modern themed widgets
- **SQLAlchemy 2.x** — ORM, declarative models
- **SQLite** — local single-file database
- **tkcalendar** — date picker
- **plyer** — cross-platform desktop notifications
- **matplotlib** — productivity charts (embedded via `FigureCanvasTkAgg`)
- **Pillow** — image / canvas support
- **PyInstaller** — packaging into a single `.exe`

Follows an **MVC architecture** with full type hints and docstrings.

---

## 📁 Project Structure

```
todo/
├── main.py                        # Application entry point
├── requirements.txt               # Pinned Python dependencies
├── README.md                      # This file
├── LICENSE                        # MIT license
├── todo_app.spec                 # PyInstaller spec (build script)
├── build.bat                     # One-click Windows build
├── .gitignore                    # Repo hygiene
└── todo_app/
    ├── __init__.py
    ├── database/                 # SQLAlchemy engine, session factory, bootstrap
    │   ├── __init__.py
    │   └── db_manager.py
    ├── models/                   # ORM models (Task, Category, AppSettings, ...)
    │   ├── __init__.py
    │   ├── task.py
    │   ├── category.py
    │   ├── settings.py
    │   ├── notification.py
    │   ├── pomodoro.py
    │   ├── backup.py
    │   └── activity.py
    ├── controllers/              # Business logic (the M in MVC)
    │   ├── __init__.py
    │   ├── task_controller.py
    │   ├── category_controller.py
    │   ├── settings_controller.py
    │   ├── statistics_controller.py
    │   ├── backup_controller.py
    │   ├── activity_controller.py
    │   └── notification_service.py
    ├── views/                    # CustomTkinter UI
    │   ├── __init__.py
    │   ├── main_window.py        # Sidebar + topbar + content shell
    │   ├── dashboard.py          # Greeting, KPIs, progress, deadlines, activity
    │   ├── task_view.py          # List, search, filter, sort, edit, drag-reorder
    │   ├── task_editor.py        # Create / edit dialog
    │   ├── quick_add.py          # Fast capture popup
    │   ├── calendar_view.py      # Month calendar + per-day task list
    │   ├── planner_view.py       # 24-hour vertical timeline
    │   ├── stats_view.py         # Matplotlib charts
    │   ├── pomodoro_view.py      # Pomodoro + stopwatch + countdown + goals
    │   ├── settings_view.py      # Preferences and backup management
    │   ├── theme.py              # Centralized palette manager
    │   ├── widgets.py            # Reusable themed widgets (Card, StatTile, ProgressRing, ...)
    │   ├── icons.py              # Emoji-based icon glyphs
    │   └── confetti.py           # Celebration overlay
    ├── utils/                    # Constants, helpers, logging, quotes
    │   ├── __init__.py
    │   ├── constants.py
    │   ├── helpers.py
    │   ├── logger.py
    │   └── quotes.py
    ├── assets/                   # (reserved) bundled assets
    ├── icons/                    # (reserved) icon files
    ├── themes/                   # (reserved) custom theme overrides
    ├── backups/                  # Created at runtime
    ├── exports/                  # Created at runtime
    └── config/                   # (reserved) app-level config
```

Runtime data (database, logs, backups) lives in `todo_app_data/` next to
`main.py` and is created automatically on first launch.

---

## 🚀 Installation

### 1. Prerequisites
- **Windows 10 / 11** (works on macOS / Linux too, but the build script targets Windows)
- **Python 3.10 or newer** — [python.org](https://www.python.org/downloads/)

### 2. Clone & install
```powershell
git clone https://github.com/holosion/todo_windows_app.git
cd todo_windows_app
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run
```powershell
python main.py
```

The first launch creates `todo_app_data/akena_todo.db` and seeds the default
categories, settings, and schema. No internet required — ever.

---

## 📦 Building a Windows `.exe`

A PyInstaller spec and a one-click batch script are included.

```powershell
.\build.bat
```

This produces `dist\AkenaTodo\AkenaTodo.exe` (or a single-file build — see the
spec). The exe is fully self-contained: drop it on any Windows 11 machine
and double-click to run.

For a single-file build:
```powershell
pyinstaller --noconfirm --clean --onefile --windowed `
    --name AkenaTodo `
    --add-data "todo_app;todo_app" `
    main.py
```

> **Note on plyer**: on Windows, plyer falls back to `win10toast`-style
> toast notifications. If toasts don't appear, the app will still play a
> system bell — never silently fails.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| --- | --- |
| `Ctrl+N` | Quick add task |
| `Ctrl+S` | Save cue (autosave is on) |
| `Ctrl+F` | Focus search |
| `Ctrl+D` | Duplicate selected task |
| `Ctrl+T` | Toggle Light / Dark theme |
| `Delete` | Delete selected task |
| `Space` | Toggle complete on selected task |

> Tip: click any task row in **Tasks** view to select it. The selection
> is preserved as you switch views.

---

## 💾 Data, Backup, Restore

- **Auto-save** — every change is committed to SQLite immediately
- **Manual backup** — Settings → Backup → *Create Backup*
- **Export** — copy the database to anywhere on disk
- **Import** — replace the current database with a `.db` file
- **Restore** — pick any saved backup in Settings and click *Restore*

All backups live under `todo_app_data/backups/` and are listed inside the
Settings view with their timestamp and size.

---

## 🗄️ Database Schema

| Table | Purpose |
| --- | --- |
| `tasks` | Every task and its full metadata |
| `categories` | User-defined categories |
| `app_settings` | Single-row JSON settings blob |
| `notifications` | Fired reminders (audit log) |
| `pomodoro_sessions` | Each completed Pomodoro phase |
| `activity_log` | Dashboard's "Recent activity" feed |
| `backups` | Metadata for saved backups |

Statistics are computed on demand from `tasks` (no stale cached aggregates).

---

## 🧪 Smoke Test

After install, run the import-time smoke check:
```powershell
python -c "from todo_app.views.main_window import MainWindow; print('OK')"
```

You should see `OK` and the app should boot into the Dashboard.

---

## 🛠️ Development Notes

- **MVC split** — views never touch the database directly; they go through
  controllers. `TaskController`, `StatisticsController`, etc. are the
  only place where SQLAlchemy queries live.
- **Theme switching** — `THEME.apply()` re-paints the palette and the
  MainWindow rebuilds active views to inherit the new colors.
- **Logging** — logs are written to `todo_app_data/logs/app.log` via
  `utils/logger.py`; every controller logs its major actions.
- **No third-party network calls** — no analytics, no telemetry, no
  auto-update pings.

---

## 📝 License

MIT — see [LICENSE](LICENSE).
