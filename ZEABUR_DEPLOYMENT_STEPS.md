# Zeabur 部署完整步驟指南

## 🎯 目前狀態

✅ **後端服務已建立**
- 服務名稱: posefit-project
- 域名: `posefit.zeabur.app`
- 狀態: Provisioning (90-120 秒)

---

## 📝 Step 1: 設定後端環境變數 (進行中)

### 1.1 複製環境變數

開啟檔案 `ZEABUR_BACKEND_ENV.txt`，複製所有環境變數。

### 1.2 在 Zeabur 新增環境變數

在 Zeabur 後端服務頁面：
1. 點選「環境變數」頁籤
2. 逐一新增以下環境變數：

```bash
DEBUG=False
SECRET_KEY=t)onv50cty$hyx%_(mc$y=k0p!n383$avn)*$pmq8%8zh-aqv-^q-@c-(_=e
DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=posefit.zeabur.app
FRONTEND_URL=https://posefit.zeabur.app
CORS_ALLOWED_ORIGINS=https://posefit.zeabur.app
CSRF_TRUSTED_ORIGINS=https://posefit.zeabur.app
DB_NAME=posefit_db
DB_USER=root
DB_PASSWORD=ytOopf10Z94IDs83X2E7Q5ilve6YxUNm
DB_HOST=mysql.zeabur.internal
DB_PORT=3306
GOOGLE_GENERATIVE_AI_API_KEY=<你的Gemini API金鑰>
PORT=${WEB_PORT}
```

### 1.3 ⚠️ 重要：填入 Gemini API 金鑰

**取得方式：**
1. 前往：https://makersuite.google.com/app/apikey
2. 登入 Google 帳號
3. 建立新的 API 金鑰
4. 複製金鑰並填入 `GOOGLE_GENERATIVE_AI_API_KEY`

### 1.4 儲存並重新部署

1. 儲存所有環境變數
2. 點選「重新部署」
3. 等待部署完成（約 2-5 分鐘）

---

## 🗄️ Step 2: 設定 MySQL 資料庫

### 2.1 新增 MySQL 服務

1. 在 Zeabur 專案頁面點選「建立服務」
2. 選擇「預建置」→「MySQL」
3. 等待 MySQL 服務啟動

### 2.2 連結資料庫到後端

1. MySQL 服務會自動注入環境變數
2. 檢查是否有以下變數（Zeabur 自動提供）：
   - `MYSQL_HOST`
   - `MYSQL_PORT`
   - `MYSQL_USERNAME`
   - `MYSQL_PASSWORD`
   - `MYSQL_DATABASE`

### 2.3 調整環境變數（如需要）

如果 Zeabur 使用 `MYSQL_*` 變數名，您有兩個選擇：

**選擇 1：** 在後端環境變數中設定對應關係
```bash
DB_HOST=${MYSQL_HOST}
DB_PORT=${MYSQL_PORT}
DB_USER=${MYSQL_USERNAME}
DB_PASSWORD=${MYSQL_PASSWORD}
DB_NAME=${MYSQL_DATABASE}
```

**選擇 2：** 修改 `backend/config/settings/production.py` 中的資料庫設定

---

## 🔧 Step 3: 初始化資料庫

### 3.1 進入後端服務終端

在 Zeabur 後端服務頁面：
1. 點選「終端」或「Console」
2. 執行以下指令

### 3.2 執行資料庫遷移

```bash
python manage.py migrate
```

### 3.3 收集靜態檔案

```bash
python manage.py collectstatic --noinput
```

### 3.4 建立超級使用者（管理員）

```bash
python manage.py createsuperuser
```

按提示輸入：
- 使用者名稱
- Email
- 密碼（兩次）

---

## 🎨 Step 4: 部署前端服務

### 4.1 建立前端服務

1. 在 Zeabur 專案頁面點選「建立服務」
2. 選擇「Git」→ 選擇 `neil930220/posefit_project`
3. 選擇 `main` 分支

### 4.2 設定前端服務

**重要設定：**

| 設定項目 | 值 |
|---------|---|
| 根目錄 (Root Directory) | `frontend` |
| 建置指令 (Build Command) | `npm install && npm run build` |
| 輸出目錄 (Output Directory) | `dist` |
| 框架 (Framework) | Vite |

### 4.3 設定前端環境變數

在前端服務的環境變數頁面新增：

```bash
VITE_API_BASE_URL=https://posefit.zeabur.app/api/
```

### 4.4 部署前端

1. 儲存設定
2. 點選「部署」
3. 等待建置完成（約 3-5 分鐘）

---

## 🔄 Step 5: 更新後端 CORS 設定（如前端使用不同域名）

### 5.1 如果前端有獨立域名

假設前端域名是 `posefit-frontend.zeabur.app`，需要更新後端環境變數：

```bash
ALLOWED_HOSTS=posefit.zeabur.app,posefit-frontend.zeabur.app
FRONTEND_URL=https://posefit-frontend.zeabur.app
CORS_ALLOWED_ORIGINS=https://posefit-frontend.zeabur.app
CSRF_TRUSTED_ORIGINS=https://posefit.zeabur.app,https://posefit-frontend.zeabur.app
```

### 5.2 重新部署後端

更新環境變數後，重新部署後端服務。

---

## ✅ Step 6: 測試部署

### 6.1 測試後端 API

訪問以下網址檢查後端是否正常：

```
https://posefit.zeabur.app/admin
```

應該會看到 Django 管理後台登入頁面。

### 6.2 測試前端

訪問前端域名，應該能看到應用程式首頁。

### 6.3 測試功能

1. **使用者註冊/登入**
2. **上傳食物照片**
3. **營養計算功能**
4. **體重記錄功能**

---

## 🎯 部署檢查清單

### 後端
- [ ] 環境變數全部設定完成
- [ ] GOOGLE_GENERATIVE_AI_API_KEY 已填入
- [ ] MySQL 服務已連結
- [ ] 資料庫遷移已執行
- [ ] 靜態檔案已收集
- [ ] 管理員帳號已建立
- [ ] 可以訪問 /admin 頁面

### 前端
- [ ] 根目錄設定為 frontend
- [ ] 建置指令正確
- [ ] VITE_API_BASE_URL 已設定
- [ ] 建置成功無錯誤
- [ ] 可以訪問前端頁面

### 整合測試
- [ ] 前端可以呼叫後端 API
- [ ] 使用者可以註冊登入
- [ ] 圖片上傳功能正常
- [ ] 沒有 CORS 錯誤

---

## 🔧 疑難排解

### 問題 1: 500 Internal Server Error

**可能原因：**
- `ALLOWED_HOSTS` 未設定或設定錯誤
- 資料庫連線失敗
- 環境變數缺失

**解決方式：**
1. 檢查 Zeabur 服務日誌
2. 確認所有環境變數已設定
3. 檢查資料庫服務是否正常

### 問題 2: CORS 錯誤

**錯誤訊息：**
```
Access to fetch at 'https://posefit.zeabur.app/api/...' from origin 'https://...' has been blocked by CORS policy
```

**解決方式：**
1. 確認 `CORS_ALLOWED_ORIGINS` 包含前端域名
2. 確認域名格式正確（包含 https://，無結尾斜線）
3. 重新部署後端服務

### 問題 3: 資料庫連線失敗

**可能原因：**
- MySQL 服務未啟動
- 資料庫環境變數錯誤

**解決方式：**
1. 檢查 MySQL 服務狀態
2. 確認環境變數名稱正確
3. 嘗試在終端連接資料庫測試

### 問題 4: 靜態檔案 404

**解決方式：**
```bash
python manage.py collectstatic --noinput
```

### 問題 5: 前端建置失敗

**可能原因：**
- Node.js 版本不符
- 依賴套件安裝失敗

**解決方式：**
1. 檢查建置日誌
2. 確認 package.json 正確
3. 確認根目錄設定為 frontend

---

## 📞 需要幫助？

如果遇到問題：
1. 查看 Zeabur 服務日誌
2. 檢查環境變數設定
3. 參考 `ZEABUR_ENV_VARIABLES.md` 詳細說明
4. 查看 GitHub Issues

---

**祝您部署順利！** 🎉

