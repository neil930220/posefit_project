@echo off
echo Setting up PoseFit Project for Windows...

REM Navigate to backend directory
cd /d "%~dp0..\backend"

REM Create Windows virtual environment
echo Creating Windows virtual environment...
py -m venv winvenv

REM Activate virtual environment
echo Activating virtual environment...
call winvenv\Scripts\activate.bat

REM Install requirements
echo Installing Python dependencies...
py -m pip install --upgrade pip
py -m pip install -r requirements/base.txt

REM Navigate to frontend directory
cd /d "%~dp0..\frontend"

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install

echo Setup complete!
echo.
echo To start the servers:
echo 1. Run: scripts\start_win.bat
echo 2. Or manually:
echo    - Backend: cd backend && winvenv\Scripts\activate && py manage.py runserver
echo    - Frontend: cd frontend && npm run dev
pause 