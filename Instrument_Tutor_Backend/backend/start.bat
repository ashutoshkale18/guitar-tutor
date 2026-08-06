@echo off
echo ============================================================
echo   Guitar Tutor Backend
echo ============================================================
echo.

REM Activate venv and start server
cd /d "%~dp0"
call venv\Scripts\activate
python main.py

pause
