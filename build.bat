@echo off
REM ============================================================
REM  Akena Todo - one-click Windows build script
REM  Produces dist\AkenaTodo\AkenaTodo.exe
REM ============================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo === Akena Todo build ===
echo.

REM --- Sanity: Python present? ------------------------------------------------
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python is not on PATH. Install Python 3.10+ and retry.
    exit /b 1
)

REM --- Activate venv if it exists --------------------------------------------
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating .venv ...
    call ".venv\Scripts\activate.bat"
)

REM --- Ensure dependencies ----------------------------------------------------
echo [INFO] Installing requirements ...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] pip install failed.
    exit /b 1
)

REM --- Clean previous build ---------------------------------------------------
echo [INFO] Cleaning previous build artifacts ...
if exist build  rmdir /s /q build
if exist dist   rmdir /s /q dist

REM --- Run PyInstaller --------------------------------------------------------
echo [INFO] Building executable with PyInstaller ...
python -m PyInstaller --noconfirm --clean --onedir --windowed ^
    --name AkenaTodo ^
    --icon "todo_app\assets\akena_todo.ico" ^
    --add-data "todo_app;todo_app" ^
    --add-data "LICENSE;LICENSE" ^
    --hidden-import customtkinter ^
    --hidden-import tkcalendar ^
    --hidden-import tkcalendar.calendar_ ^
    --hidden-import plyer ^
    --hidden-import plyer.platforms ^
    --hidden-import plyer.platforms.win.notification ^
    --hidden-import matplotlib ^
    --hidden-import matplotlib.backends.backend_tkagg ^
    --hidden-import PIL ^
    --hidden-import PIL._tkinter_finder ^
    --hidden-import sqlalchemy.dialects.sqlite ^
    --hidden-import sqlalchemy.orm.strategies ^
    --hidden-import pystray ^
    --hidden-import todo_app ^
    --hidden-import todo_app.database ^
    --hidden-import todo_app.models ^
    --hidden-import todo_app.controllers ^
    --hidden-import todo_app.views ^
    --hidden-import todo_app.utils ^
    --exclude-module numpy.tests ^
    --exclude-module matplotlib.tests ^
    --exclude-module PIL.tests ^
    --exclude-module scipy ^
    --exclude-module pandas ^
    --exclude-module pytest ^
    --exclude-module setuptools ^
    main.py
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    exit /b 1
)

echo.
echo === Build complete ===
echo Output: dist\AkenaTodo\AkenaTodo.exe
echo.
endlocal
exit /b 0
