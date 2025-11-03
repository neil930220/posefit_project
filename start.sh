#!/bin/bash

export PYTHONUNBUFFERED=1
export DJANGO_SETTINGS_MODULE=config.settings.production

cd /app/backend

echo "Running migrations..."
python manage.py migrate --noinput || true

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Starting Gunicorn..."
gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 120 &

echo "Starting Nginx..."
exec nginx -g "daemon off;"
