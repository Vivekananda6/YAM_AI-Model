@echo off
setlocal
cd /d "%~dp0"
if exist "dist\YAM_AI_Assistant.exe" (
    start "YAM AI Assistant" "dist\YAM_AI_Assistant.exe"
    exit /b 0
)
set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"
"%PYTHON_EXE%" --version >nul 2>nul
if errorlevel 1 (
    echo Python is not installed or is not on PATH.
    echo Install Python and project dependencies, or build dist\YAM_AI_Assistant.exe.
    pause
    exit /b 1
)
"%PYTHON_EXE%" "AI_YAM\AI_YAM.py"
if errorlevel 1 pause
