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

# 下載大型模型檔（在建置階段將模型打包進映像）
RUN mkdir -p /app/backend/ml_models/models && \
    gdown "https://drive.google.com/uc?id=1J2EFlwaIMYiy93CYWCsU-A2P_8M3qLC8" -O /app/backend/ml_models/models/foodseg103_resnet50_attention.pth
# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# 進入 backend 目錄
WORKDIR /app/backend

# 收集靜態檔案（建置時執行）
RUN python manage.py collectstatic --noinput || true

# 複製啟動腳本
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# 暴露端口
EXPOSE 8080

# 啟動指令
CMD ["/app/start.sh"]

