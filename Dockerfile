# 第一階段：建置 Python 應用
FROM python:3.12-slim AS builder

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    default-libmysqlclient-dev \
    pkg-config \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements 檔案
COPY backend/requirements/base.txt /app/backend/requirements/base.txt
COPY backend/requirements/production.txt /app/backend/requirements/production.txt

# 安裝 Python 依賴
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend/requirements/production.txt

# 複製整個專案
COPY . /app/

# 下載大型模型檔
RUN mkdir -p /app/backend/ml_models/models && \
    gdown "https://drive.google.com/uc?id=1J2EFlwaIMYiy93CYWCsU-A2P_8M3qLC8" -O /app/backend/ml_models/models/foodseg103_resnet50_attention.pth

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app/backend

# 收集靜態檔案
RUN python manage.py collectstatic --noinput || true

# 第二階段：Nginx + Gunicorn
FROM python:3.12-slim

# 安裝 Nginx 和必要的工具
RUN apt-get update && apt-get install -y \
    nginx \
    gcc \
    g++ \
    default-libmysqlclient-dev \
    pkg-config \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 從建置階段複製 Python 依賴和應用
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /app /app

# 建立 Nginx 配置（包含 CORS 支持）
RUN mkdir -p /etc/nginx/sites-enabled && \
    rm -f /etc/nginx/sites-enabled/default

RUN cat > /etc/nginx/sites-enabled/default << 'NGINX_EOF'
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 8080;
    server_name _;
    client_max_body_size 100M;

    # 靜態檔案
    location /static/ {
        alias /app/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        add_header 'Access-Control-Allow-Origin' 'https://posefit-project-frontend.zeabur.app' always;
    }

    # 媒體檔案
    location /media/ {
        alias /app/backend/media/;
        expires 7d;
        add_header Cache-Control "public";
        add_header 'Access-Control-Allow-Origin' 'https://posefit-project-frontend.zeabur.app' always;
    }

    # Django 應用
    location / {
        # CORS 響應頭
        add_header 'Access-Control-Allow-Origin' 'https://posefit-project-frontend.zeabur.app' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, PATCH, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization, X-Requested-With, Accept' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        add_header 'Access-Control-Max-Age' '86400' always;

        # 處理 OPTIONS 預檢請求
        if ($request_method = 'OPTIONS') {
            return 204;
        }

        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
NGINX_EOF

# 複製啟動腳本
RUN cat > /app/start.sh << 'START_EOF'
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
START_EOF

RUN chmod +x /app/start.sh

EXPOSE 8080

CMD ["/app/start.sh"]