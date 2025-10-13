# 使用 Python 3.12 作為基礎映像
FROM python:3.12-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    default-libmysqlclient-dev \
    pkg-config \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements 檔案
COPY backend/requirements/base.txt /app/backend/requirements/base.txt
COPY backend/requirements/production.txt /app/backend/requirements/production.txt

# 安裝 Python 依賴
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend/requirements/production.txt

# 複製整個專案
COPY . /app/

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# 進入 backend 目錄
WORKDIR /app/backend

# 收集靜態檔案（建置時執行）
RUN python manage.py collectstatic --noinput || true

# 暴露端口
EXPOSE 8080

# 啟動指令
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "3", "--timeout", "120"]

