# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('todo_app', 'todo_app'), ('LICENSE', 'LICENSE')],
    hiddenimports=['customtkinter', 'tkcalendar', 'tkcalendar.calendar_', 'plyer', 'plyer.platforms', 'plyer.platforms.win.notification', 'matplotlib', 'matplotlib.backends.backend_tkagg', 'PIL', 'PIL._tkinter_finder', 'sqlalchemy.dialects.sqlite', 'sqlalchemy.orm.strategies', 'pystray', 'todo_app', 'todo_app.database', 'todo_app.models', 'todo_app.controllers', 'todo_app.views', 'todo_app.utils'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['numpy.tests', 'matplotlib.tests', 'PIL.tests', 'scipy', 'pandas', 'pytest', 'setuptools'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AkenaTodo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AkenaTodo',
)
