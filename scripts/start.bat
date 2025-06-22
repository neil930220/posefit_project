@echo off
setlocal enabledelayedexpansion

echo 🚀 Starting FoodCam development servers...

REM Store the root directory
set "ROOT_DIR=%~dp0.."
cd "%ROOT_DIR%"

REM Check if virtual environment exists
if not exist "backend\venv" (
    echo ❌ Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call backend\venv\Scripts\activate

REM Start Django backend server
echo 🌐 Starting Django backend server...
start cmd /k "cd /d "%ROOT_DIR%\backend" && python manage.py runserver"

REM Start Vue.js frontend server
echo 🎨 Starting Vue.js frontend server...
start cmd /k "cd /d "%ROOT_DIR%\frontend" && npm run dev"

echo ✅ Servers started!
echo.
echo 🌐 Access points:
echo    Frontend: http://localhost:5173
echo    Backend:  http://localhost:8000
echo    Admin:    http://localhost:8000/admin
echo.
echo Press any key to close this window...
pause > nul 