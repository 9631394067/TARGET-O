@echo off
setlocal
title Indian Journal Citation Parser

REM ── Get the folder where this bat file is ──────────────
set "PROJECT_DIR=%~dp0"
set "PYTHON=%PROJECT_DIR%venv\Scripts\python.exe"
set "MAIN=%PROJECT_DIR%main.py"

cls
color 0A
echo.
echo  ====================================================
echo    INDIAN JOURNAL CITATION PARSER
echo    Automated DOI and Citation Metadata Parser
echo  ====================================================
echo.

REM ── Check Python venv ───────────────────────────────────
if not exist "%PYTHON%" (
    echo  [ERROR] venv not found at: %PYTHON%
    echo.
    echo  Please run this first:
    echo    python -m venv venv
    echo    venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM ── Check main.py ───────────────────────────────────────
if not exist "%MAIN%" (
    echo  [ERROR] main.py not found at: %MAIN%
    pause
    exit /b 1
)

echo  [OK] Project folder : %PROJECT_DIR%
echo  [OK] Python venv    : Found
echo  [OK] main.py        : Found
echo.
echo  ────────────────────────────────────────────────────
echo   Server starting...
echo  ────────────────────────────────────────────────────
echo.
echo   Open in browser:
echo.
echo   Frontend  ^>  http://localhost:8000
echo   API Docs  ^>  http://localhost:8000/docs
echo   Health    ^>  http://localhost:8000/api/v1/health
echo.
echo   Press Ctrl+C to stop
echo  ────────────────────────────────────────────────────
echo.

REM ── Open browser after 3 seconds ───────────────────────
start "" timeout /t 3 /nobreak >nul 2>&1
start "" "http://localhost:8000"

REM ── Start the server ─────────────────────────────────── 
cd /d "%PROJECT_DIR%"
"%PYTHON%" "%MAIN%"

echo.
echo  Server stopped.
pause
endlocal
