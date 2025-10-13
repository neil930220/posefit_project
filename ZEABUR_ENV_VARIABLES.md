# Zeabur 環境變數設定清單

## 📝 後端 (Backend Service) 環境變數

請在 Zeabur 後端服務的環境變數設定中，逐一新增以下變數：

---

### 🔴 必要設定 (Required)

| 變數名稱 | 說明 | 範例值 | 備註 |
|---------|------|--------|------|
| `DEBUG` | Django 除錯模式 | `False` | ⚠️ 生產環境必須設為 False |
| `SECRET_KEY` | Django 密鑰 | `your-super-secret-key-at-least-50-chars` | ⚠️ 請使用強密鑰 |
| `DJANGO_SETTINGS_MODULE` | Django 設定模組 | `config.settings.production` | 使用生產環境設定 |
| `ALLOWED_HOSTS` | 允許的主機名稱 | `your-backend.zeabur.app,your-frontend.zeabur.app` | 多個域名用逗號分隔 |
| `FRONTEND_URL` | 前端網址 | `https://your-frontend.zeabur.app` | 完整 URL 包含 https:// |
| `CORS_ALLOWED_ORIGINS` | CORS 允許來源 | `https://your-frontend.zeabur.app` | 多個來源用逗號分隔 |
| `CSRF_TRUSTED_ORIGINS` | CSRF 信任來源 | `https://your-frontend.zeabur.app,https://your-backend.zeabur.app` | 多個來源用逗號分隔 |

---

### 🗄️ 資料庫設定 (Database) - Zeabur MySQL

⚠️ **重要：** 如果您在 Zeabur 使用 MySQL 服務，這些變數會自動注入，通常不需要手動設定。  
但如果需要手動設定，請使用以下變數：

| 變數名稱 | 說明 | 範例值 |
|---------|------|--------|
| `DB_NAME` | 資料庫名稱 | `posefit_db` |
| `DB_USER` | 資料庫使用者 | `root` |
| `DB_PASSWORD` | 資料庫密碼 | `your-db-password` |
| `DB_HOST` | 資料庫主機 | `mysql.zeabur.internal` |
| `DB_PORT` | 資料庫埠號 | `3306` |

**Zeabur MySQL 服務通常會自動提供以下環境變數：**
- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_USERNAME`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`

如果 Zeabur 使用這些變數名，您可能需要在 `backend/config/settings/production.py` 中調整變數名稱對應。

---

### 🤖 API 金鑰 (API Keys)

| 變數名稱 | 說明 | 取得方式 | 備註 |
|---------|------|---------|------|
| `GOOGLE_GENERATIVE_AI_API_KEY` | Google Gemini AI API 金鑰 | https://makersuite.google.com/app/apikey | ⚠️ 必要，用於食物營養分析 |

---

### 📧 郵件設定 (Email) - 選用

如果需要寄送郵件功能（如密碼重設），請設定：

| 變數名稱 | 說明 | 範例值 |
|---------|------|--------|
| `EMAIL_BACKEND` | 郵件後端 | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | SMTP 伺服器 | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP 埠號 | `587` |
| `EMAIL_HOST_USER` | 郵件帳號 | `your-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | 郵件密碼 | `your-app-specific-password` |

**Gmail 應用程式密碼取得方式：**
1. 開啟 Google 帳戶安全性設定
2. 啟用兩步驟驗證
3. 建立應用程式密碼
4. 使用應用程式密碼（非原始密碼）

---

### 🚀 快取設定 (Cache) - 選用

如果需要使用 Redis 快取，請設定：

| 變數名稱 | 說明 | 範例值 |
|---------|------|--------|
| `REDIS_URL` | Redis 連線 URL | `redis://redis.zeabur.internal:6379/1` |

---

## 🎨 前端 (Frontend Service) 環境變數

### 方式一：在 Zeabur 前端服務設定

| 變數名稱 | 說明 | 範例值 |
|---------|------|--------|
| `VITE_API_BASE_URL` | 後端 API 網址 | `https://your-backend.zeabur.app/api/` |

### 方式二：修改 `frontend/.env.production` 檔案

已建立 `frontend/.env.production` 檔案，請修改其中的 URL 為您的實際後端網址。

---

## 🔐 密鑰生成建議

### 生成 Django SECRET_KEY

**方法一：使用 Python**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**方法二：線上生成**
- https://djecrety.ir/

**要求：**
- 至少 50 個字元
- 包含大小寫字母、數字、特殊符號
- 絕對不要使用開發環境的密鑰

---

## 📋 快速設定檢查清單

### 後端環境變數（必須設定）

```bash
# 複製以下內容到 Zeabur 後端服務的環境變數設定中
# ⚠️ 請替換所有 <YOUR_XXX> 為實際值

DEBUG=False
SECRET_KEY=<YOUR_GENERATED_SECRET_KEY>
DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=<YOUR_BACKEND_DOMAIN>.zeabur.app,<YOUR_FRONTEND_DOMAIN>.zeabur.app
FRONTEND_URL=https://<YOUR_FRONTEND_DOMAIN>.zeabur.app
CORS_ALLOWED_ORIGINS=https://<YOUR_FRONTEND_DOMAIN>.zeabur.app
CSRF_TRUSTED_ORIGINS=https://<YOUR_FRONTEND_DOMAIN>.zeabur.app,https://<YOUR_BACKEND_DOMAIN>.zeabur.app
GOOGLE_GENERATIVE_AI_API_KEY=<YOUR_GEMINI_API_KEY>

# 資料庫設定（如果 Zeabur 沒有自動注入）
DB_NAME=posefit_db
DB_USER=root
DB_PASSWORD=<ZEABUR_MYSQL_PASSWORD>
DB_HOST=<ZEABUR_MYSQL_HOST>
DB_PORT=3306
```

### 前端環境變數（必須設定）

在 Zeabur 前端服務設定或修改 `frontend/.env.production`：

```bash
VITE_API_BASE_URL=https://<YOUR_BACKEND_DOMAIN>.zeabur.app/api/
```

---

## 🎯 設定步驟

### 1. 後端服務

1. 在 Zeabur 建立後端服務（從 GitHub repo）
2. 新增 MySQL 服務並連結到後端
3. 在後端服務的「環境變數」頁面，逐一新增上述必要變數
4. 部署後端服務
5. 執行資料庫遷移（可能需要在 Zeabur 的終端執行）：
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser  # 建立管理員帳號
   ```

### 2. 前端服務

1. 在 Zeabur 建立前端服務（從同一個 GitHub repo）
2. 設定根目錄為 `frontend`
3. 建置指令：`npm install && npm run build`
4. 輸出目錄：`dist`
5. 設定環境變數 `VITE_API_BASE_URL`
6. 部署前端服務

### 3. 域名設定

1. 在 Zeabur 為前端和後端服務設定域名
2. 將域名更新到環境變數中（`ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` 等）
3. 重新部署服務

---

## ⚠️ 重要注意事項

1. **絕對不要**在程式碼中寫死任何密鑰或密碼
2. **絕對不要**將包含真實密鑰的 `.env` 檔案提交到 Git
3. **確保** `DEBUG=False` 在生產環境
4. **確保** 所有域名都加入 `ALLOWED_HOSTS` 和 CORS 設定
5. **確保** HTTPS 在生產環境中啟用（Zeabur 預設提供）
6. **定期更換** SECRET_KEY 和其他敏感憑證
7. **備份**資料庫定期備份

---

## 🔧 疑難排解

### 問題：500 Internal Server Error

**檢查：**
- `DEBUG=False` 時確保 `ALLOWED_HOSTS` 設定正確
- 檢查資料庫連線是否正常
- 查看 Zeabur 服務日誌

### 問題：CORS 錯誤

**檢查：**
- `CORS_ALLOWED_ORIGINS` 是否包含前端域名
- 域名必須包含 `https://` 且不能有結尾斜線
- 多個域名用逗號分隔

### 問題：資料庫連線失敗

**檢查：**
- Zeabur MySQL 服務是否已啟動
- 環境變數名稱是否正確（Zeabur 可能使用 `MYSQL_*` 而非 `DB_*`）
- 網路連線是否已設定

### 問題：靜態檔案無法載入

**解決：**
```bash
python manage.py collectstatic --noinput
```

確保 Zeabur 建置時執行此指令。

---

**最後更新：** 2025-10-13  
**版本：** v1.0.0

