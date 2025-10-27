#!/bin/bash

# 設定環境變數
export PYTHONUNBUFFERED=1
export DJANGO_SETTINGS_MODULE=config.settings.production

# 進入 backend 目錄
cd /app/backend

# 執行 migrations
echo "Running migrations..."
python manage.py migrate --noinput || true

# 執行 collectstatic（如果需要）
echo "Collecting static files..."
python manage.py collectstatic --noinput || true

# 啟動 Gunicorn
echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8080 --workers 3 --timeout 120
