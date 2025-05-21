@echo off
setlocal

REM First Git Bash window: Django backend
start "" "C:\Program Files\Git\git-bash.exe" -c "source venv/Scripts/activate && python manage.py runserver_plus --cert cert.crt --key cert.key 0.0.0.0:8000"

REM Second Git Bash window: Vue frontend
start "" "C:\Program Files\Git\git-bash.exe" -c "cd frontend && source ../venv/Scripts/activate && npx vite --mode showcase"
