@echo off
title EventFlow - Event Management System
color 0A
echo.
echo  ========================================
echo    ⚡ EventFlow - Starting Server...
echo  ========================================
echo.

cd /d "%~dp0"

echo  [1/2] Seeding Database...
python seed.py 2>nul
echo.

echo  [2/2] Starting Server...
echo.
echo  ========================================
echo   Server is LIVE!
echo   Open this URL in your browser:
echo.
echo   👉  http://127.0.0.1:5000
echo.
echo   Login Credentials:
echo   Admin:     admin@eventflow.com / admin123
echo   Organizer: organizer@eventflow.com / org123
echo   Attendee:  user@eventflow.com / user123
echo  ========================================
echo.
echo  Press Ctrl+C to stop the server.
echo.

start http://127.0.0.1:5000
python run.py

pause
