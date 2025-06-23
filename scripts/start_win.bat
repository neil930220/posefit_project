@echo off
echo Starting PoseFit Project servers...

REM Start Django backend server in a new window
echo Starting Django backend server...
start "Django Backend" cmd /k "cd /d "%~dp0..\backend" && winvenv\Scripts\activate && py manage.py runserver"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start Vue.js frontend server in a new window
echo Starting Vue.js frontend server...
start "Vue.js Frontend" cmd /k "cd /d "%~dp0..\frontend" && npm run dev"

echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to close this window (servers will continue running)
pause >nul 