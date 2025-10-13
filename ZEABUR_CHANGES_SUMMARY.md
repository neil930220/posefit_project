# Zeabur 部署 - 快速修改參考表

## 📍 需要修改的檔案清單（共 7 個檔案）

⚠️ **目前尚未修改任何檔案**

---

## 🔴 必須修改的檔案

### 1. `backend/manage.py`
```python
# 第 9 行
# 從：
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# 改為：
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
```

---

### 2. `backend/config/wsgi.py`
```python
# 第 14 行
# 從：
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# 改為：
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
```

---

### 3. `backend/config/asgi.py`
```python
# 第 14 行
# 從：
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# 改為：
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
```

---

## 🟡 需要新增的檔案

### 4. `frontend/.env.production` (新建檔案)
```bash
# 新增這個檔案，內容如下：
VITE_API_BASE_URL=https://你的後端域名.zeabur.app/api/
```

---

### 5. `backend/.env` (Zeabur 環境變數設定)
在 Zeabur 後台設定以下環境變數：

```bash
# 基本設定
DEBUG=False
SECRET_KEY=你的超強密鑰
DJANGO_SETTINGS_MODULE=config.settings.production

# 主機設定
ALLOWED_HOSTS=你的域名.zeabur.app
FRONTEND_URL=https://你的域名.zeabur.app

# CORS 設定
CORS_ALLOWED_ORIGINS=https://你的域名.zeabur.app
CSRF_TRUSTED_ORIGINS=https://你的域名.zeabur.app

# 資料庫設定 (Zeabur MySQL 會自動提供)
DB_NAME=zeabur提供
DB_USER=zeabur提供
DB_PASSWORD=zeabur提供
DB_HOST=zeabur提供
DB_PORT=3306

# API 金鑰
GOOGLE_GENERATIVE_AI_API_KEY=你的Gemini金鑰
```

---

## 🟢 參考用（不需修改，但要了解）

### 6. `backend/config/settings/development.py`
這個檔案包含所有本地環境設定，**不需要修改**，但要知道這些是本地設定：
- 行 13: `ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.12.165']`
- 行 16: `FRONTEND_URL = 'http://localhost:5173'`
- 行 21-23: CORS 本地設定
- 行 26-28: CSRF 本地設定

### 7. `backend/config/settings/production.py`
這個檔案已經配置好生產環境設定，**不需要修改**，會從環境變數讀取。

### 8. `frontend/src/services/api.js`
這個檔案**不需要修改**，因為它會自動讀取環境變數：
- 行 11: `baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/'`
- 只要設定好 `VITE_API_BASE_URL` 環境變數即可

### 9. `frontend/vite.config.js`
這個檔案的 proxy 設定**只在開發環境使用**，生產環境建置時會忽略，不需要修改。

---

## 📊 修改統計

| 類別 | 數量 | 說明 |
|-----|------|------|
| 必須修改的檔案 | 3 | manage.py, wsgi.py, asgi.py |
| 需要新增的檔案 | 1 | frontend/.env.production |
| 環境變數設定 | 15+ | 在 Zeabur 後台設定 |
| 參考檔案 | 4 | 了解即可，不需修改 |

---

## 🎯 部署步驟簡化版

### Step 1: 修改 3 個檔案
```bash
# 將 development 改為 production
backend/manage.py (第 9 行)
backend/config/wsgi.py (第 14 行)
backend/config/asgi.py (第 14 行)
```

### Step 2: 新增前端環境變數檔案
```bash
# 建立檔案
frontend/.env.production

# 內容
VITE_API_BASE_URL=https://你的後端域名.zeabur.app/api/
```

### Step 3: 在 Zeabur 設定環境變數
- 至少需要設定：DEBUG, SECRET_KEY, ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS, CSRF_TRUSTED_ORIGINS
- 資料庫變數由 Zeabur MySQL 服務自動提供
- 記得設定 GOOGLE_GENERATIVE_AI_API_KEY

### Step 4: 部署
```bash
# 推送到 Zeabur
# Zeabur 會自動執行：
- pip install -r requirements/production.txt
- python manage.py migrate
- python manage.py collectstatic --noinput
- npm run build (前端)
```

---

## 🔗 相關檔案連結

- 完整部署清單：`ZEABUR_DEPLOYMENT_CHECKLIST.md`
- 後端設定檔：`backend/config/settings/production.py`
- 前端 API 設定：`frontend/src/services/api.js`
- 環境變數範本：`backend/env.example`

---

**狀態：** ⚠️ 資料收集完成，尚未進行任何修改  
**下一步：** 等待確認後開始修改檔案

