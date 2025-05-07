@echo off
setlocal

REM First Git Bash window: Django backend
start "" "C:\Program Files\Git\git-bash.exe" -c "source venv/Scripts/activate && python manage.py runserver"

REM Second Git Bash window: Vue frontend
start "" "C:\Program Files\Git\git-bash.exe" -c "cd frontend && source ../venv/Scripts/activate && npm run dev"
