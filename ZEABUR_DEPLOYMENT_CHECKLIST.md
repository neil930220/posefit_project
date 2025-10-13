# Zeabur 雲端部署配置清單

## 📋 部署前需要修改的配置

本文件記錄所有需要從本地環境改為雲端環境的配置項目。**目前尚未修改，僅供參考。**

---

## 🎯 一、後端 Django 配置

### 1.1 Django Settings 模組設定

**影響檔案：**
- `backend/manage.py` (第 9 行)
- `backend/config/wsgi.py` (第 14 行)
- `backend/config/asgi.py` (第 14 行)

**目前配置：**
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
```

**需要改為：**
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
```

---

### 1.2 生產環境設定檔

**檔案路徑：** `backend/config/settings/production.py`

**需要透過環境變數設定的項目：**

| 環境變數名稱 | 用途 | 範例值 | 行號 |
|------------|------|--------|------|
| `SECRET_KEY` | Django 密鑰 | `your-super-secret-key-here` | 12 |
| `ALLOWED_HOSTS` | 允許的主機名稱 | `yourdomain.zeabur.app,yourdomain.com` | 14 |
| `FRONTEND_URL` | 前端網址 | `https://yourdomain.zeabur.app` | 17 |
| `CORS_ALLOWED_ORIGINS` | CORS 允許來源 | `https://yourdomain.zeabur.app` | 21 |
| `CSRF_TRUSTED_ORIGINS` | CSRF 信任來源 | `https://yourdomain.zeabur.app` | 22 |
| `DB_NAME` | 資料庫名稱 | Zeabur MySQL 提供 | - |
| `DB_USER` | 資料庫使用者 | Zeabur MySQL 提供 | - |
| `DB_PASSWORD` | 資料庫密碼 | Zeabur MySQL 提供 | - |
| `DB_HOST` | 資料庫主機 | Zeabur MySQL 提供 | - |
| `DB_PORT` | 資料庫埠號 | `3306` | - |
| `REDIS_URL` | Redis 連線 | `redis://...` (選用) | 90 |
| `EMAIL_HOST` | 郵件伺服器 | `smtp.gmail.com` | 44 |
| `EMAIL_PORT` | 郵件埠號 | `587` | 45 |
| `EMAIL_HOST_USER` | 郵件帳號 | `your-email@gmail.com` | 47 |
| `EMAIL_HOST_PASSWORD` | 郵件密碼 | `your-app-password` | 48 |

---

### 1.3 開發環境設定（本地參數）

**檔案路徑：** `backend/config/settings/development.py`

**本地 IP 地址（需移除）：**
- 第 13 行：`ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.12.165']`
- 第 16 行：`FRONTEND_URL = 'http://localhost:5173'`
- 第 20-23 行：CORS 允許來源包含本地 IP
- 第 25-28 行：CSRF 信任來源包含本地 IP
- 第 34 行：`dev_server_host = "192.168.12.165"`

---

### 1.4 資料庫配置

**檔案路徑：** `backend/config/settings/base.py` (第 86-98 行)

**目前配置：**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
```

**需要設定的 Zeabur 環境變數：**
- Zeabur 會自動提供 MySQL 服務，需要將連線資訊設定到環境變數中

---

### 1.5 靜態檔案和媒體檔案

**檔案路徑：** `backend/config/settings/base.py` (第 133-142 行)

**目前配置：**
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**雲端部署考量：**
- 需要執行 `python manage.py collectstatic` 收集靜態檔案
- 媒體檔案可能需要使用 S3 或其他雲端儲存（Zeabur 預設檔案系統不持久）

---

## 🎨 二、前端 Vue.js 配置

### 2.1 API 基礎 URL

**檔案路徑：** `frontend/src/services/api.js`

**目前配置（第 11 行）：**
```javascript
baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/',
```

**目前配置（第 64 行）：**
```javascript
`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}/token/refresh/`
```

**需要設定的環境變數：**
- `VITE_API_BASE_URL` = `https://your-backend.zeabur.app/api/`

**或者建立前端環境變數檔案：**
- `.env.production` 檔案（目前不存在）

---

### 2.2 Vite 開發伺服器配置

**檔案路徑：** `frontend/vite.config.js`

**本地代理設定（第 27-48 行）：**
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',  // ← 本地後端
    changeOrigin: true,
    secure: false
  },
  // ... 其他代理
}
```

**雲端部署考量：**
- 生產環境建置（`npm run build`）時不使用 proxy
- 需要設定 `VITE_API_BASE_URL` 環境變數指向雲端後端

---

## 🔐 三、環境變數檔案

### 3.1 後端環境變數範本

**檔案路徑：** `backend/env.example`

**需要在 Zeabur 設定的環境變數：**

```bash
# Django Settings
DEBUG=False
SECRET_KEY=<生成一個新的強密鑰>
ALLOWED_HOSTS=<你的域名>.zeabur.app
DJANGO_SETTINGS_MODULE=config.settings.production

# Database (Zeabur MySQL 服務會自動提供)
DB_NAME=<zeabur提供>
DB_USER=<zeabur提供>
DB_PASSWORD=<zeabur提供>
DB_HOST=<zeabur提供>
DB_PORT=3306

# API Keys
GOOGLE_GENERATIVE_AI_API_KEY=<你的Gemini API金鑰>

# CORS Settings
CORS_ALLOWED_ORIGINS=https://<你的域名>.zeabur.app
CSRF_TRUSTED_ORIGINS=https://<你的域名>.zeabur.app

# Frontend URL
FRONTEND_URL=https://<你的域名>.zeabur.app

# Email (選用)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=<你的郵箱>
EMAIL_HOST_PASSWORD=<應用程式密碼>
```

---

### 3.2 前端環境變數

**需要建立檔案：** `frontend/.env.production`（目前不存在）

**內容範例：**
```bash
VITE_API_BASE_URL=https://<你的後端域名>.zeabur.app/api/
```

---

## 📦 四、部署相關檔案

### 4.1 Python 依賴套件

**檔案路徑：** `backend/requirements/production.txt`

**需要確認包含：**
- gunicorn（WSGI 伺服器）
- mysqlclient（MySQL 驅動）
- 所有 base.txt 的依賴

---

### 4.2 啟動腳本配置

**檔案路徑：** `scripts/start_linux.sh`

**目前配置（第 14 行）：**
```bash
python manage.py runserver
```

**生產環境應改為：**
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

---

## 🔍 五、硬編碼位置總結

### 本地 localhost 出現位置：

1. **backend/config/settings/development.py**
   - 行 13, 16, 21, 22, 26, 27

2. **frontend/src/services/api.js**
   - 行 11, 64

3. **frontend/vite.config.js**
   - 行 29, 34, 39, 44

### 本地 IP (192.168.12.165) 出現位置：

1. **backend/config/settings/development.py**
   - 行 13, 22, 27, 34

---

## ✅ 部署檢查清單

### 階段一：準備環境變數
- [ ] 在 Zeabur 設定所有必要的環境變數
- [ ] 生成新的 SECRET_KEY
- [ ] 設定資料庫連線資訊
- [ ] 設定 CORS 和 CSRF 信任域名
- [ ] 設定 Google Gemini API 金鑰

### 階段二：修改配置檔案
- [ ] 修改 manage.py 使用 production settings
- [ ] 修改 wsgi.py 使用 production settings
- [ ] 修改 asgi.py 使用 production settings
- [ ] 建立 frontend/.env.production 檔案
- [ ] 設定 VITE_API_BASE_URL

### 階段三：資料庫準備
- [ ] 執行 migrations
- [ ] 建立 superuser
- [ ] 收集靜態檔案 (collectstatic)

### 階段四：測試
- [ ] 測試後端 API 可訪問
- [ ] 測試前端可連接後端
- [ ] 測試使用者註冊/登入
- [ ] 測試圖片上傳功能
- [ ] 測試營養計算功能

---

## 🚨 重要注意事項

1. **絕對不要**將生產環境的 SECRET_KEY 提交到 Git
2. **絕對不要**在生產環境啟用 DEBUG=True
3. Zeabur 的檔案系統不持久化，媒體檔案需要使用雲端儲存
4. 需要設定正確的 ALLOWED_HOSTS 防止 HTTP Host header 攻擊
5. 確保所有 HTTPS 相關的安全設定都已啟用（production.py 中已設定）

---

## 📝 額外建議

1. **日誌記錄：** production.py 已設定檔案日誌，但 Zeabur 可能無法持久化，建議改用雲端日誌服務
2. **快取：** production.py 設定了 Redis 快取，如需使用請在 Zeabur 啟用 Redis 服務
3. **媒體檔案：** 考慮使用 AWS S3、Cloudflare R2 或其他雲端儲存
4. **監控：** 建議設定 Sentry 或其他錯誤監控服務

---

**建立時間：** 2025-10-13  
**狀態：** ⚠️ 尚未修改，僅記錄需要變更的項目

