# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Akena Todo.

Build with:
    pyinstaller --noconfirm --clean build.spec

Output:  dist\\AkenaTodo\\AkenaTodo.exe   (onedir, recommended)
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(SPECPATH).resolve()

block_cipher = None

# ---------------------------------------------------------------------------
# Hidden imports — third-party libs that PyInstaller's static analysis misses
# ---------------------------------------------------------------------------
hiddenimports = [
    "customtkinter",
    "tkcalendar",
    "tkcalendar.calendar_",
    "plyer",
    "plyer.platforms",
    "plyer.platforms.win.notification",
    "plyer.platforms.linux.notification",
    "plyer.platforms.macosx.notification",
    "matplotlib",
    "matplotlib.backends.backend_tkagg",
    "PIL",
    "PIL._tkinter_finder",
    "sqlalchemy.dialects.sqlite",
    "sqlalchemy.orm.strategies",
    # The Todo app's own packages — be explicit so PyInstaller doesn't drop them
    "todo_app",
    "todo_app.database",
    "todo_app.models",
    "todo_app.controllers",
    "todo_app.views",
    "todo_app.utils",
]

# ---------------------------------------------------------------------------
# Data files — bundle the app package, themes, icons, etc.
# ---------------------------------------------------------------------------
datas = [
    (str(PROJECT_ROOT / "todo_app"), "todo_app"),
    (str(PROJECT_ROOT / "LICENSE"),  "LICENSE"),
]

# ---------------------------------------------------------------------------
# Analysis & build
# ---------------------------------------------------------------------------
a = Analysis(
    [str(PROJECT_ROOT / "main.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Trim down the binary by skipping things the app doesn't use
        "numpy.tests",
        "matplotlib.tests",
        "PIL.tests",
        "scipy",
        "pandas",
        "pytest",
        "setuptools",
    ],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AkenaTodo",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,            # GUI app — no console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,                # Add an .ico path here if you ship one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="AkenaTodo",
)
