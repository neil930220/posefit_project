# 修復 CORS 和 WebSocket 錯誤

## 問題說明

在 Zeabur 部署後遇到兩個問題：

1. **CORS 錯誤**: 前端 `https://posefit-project-frontend.zeabur.app` 無法訪問後端 `https://posefit.zeabur.app` 的 API
2. **WebSocket 混合內容錯誤**: HTTPS 頁面嘗試連接不安全的 `ws://` WebSocket

## 解決方案

### 步驟 1: 更新前端代碼（已修復）

已移除 Vite 配置中的硬編碼 HMR 協議設定，讓 Vite 自動偵測使用 `ws://` 或 `wss://`。

**修改的檔案**: `frontend/vite.config.js`

### 步驟 2: 更新 Nginx 配置（已修復）

移除 Nginx 中硬編碼的 CORS 標頭，讓 Django CORS 中介軟體統一處理。

**修改的檔案**: `Dockerfile`

### 步驟 3: 更新 Zeabur 後端環境變數（需要手動操作）

⚠️ **重要**: 請在 Zeabur 後端服務的環境變數中更新以下設定

#### 方法 A: 逐個更新環境變數

1. 登入 [Zeabur](https://dash.zeabur.com/)
2. 進入後端服務 `posefit-project`
3. 點擊「環境變數」(Environment Variables)
4. 更新以下變數：

```env
ALLOWED_HOSTS=posefit.zeabur.app,posefit-project-frontend.zeabur.app

FRONTEND_URL=https://posefit-project-frontend.zeabur.app

CORS_ALLOWED_ORIGINS=https://posefit.zeabur.app,https://posefit-project-frontend.zeabur.app

CSRF_TRUSTED_ORIGINS=https://posefit.zeabur.app,https://posefit-project-frontend.zeabur.app
```

5. 點擊「儲存」並重新部署服務

#### 方法 B: 檢查完整的環境變數設定

參考 `ZEABUR_BACKEND_ENV.txt` 檔案，確保所有環境變數都已正確設定。

### 步驟 4: 重新部署

#### 重新部署後端

```bash
# 提交更改
git add Dockerfile ZEABUR_BACKEND_ENV.txt
git commit -m "fix: Update CORS settings and remove hardcoded Nginx CORS headers"
git push origin main
```

Zeabur 會自動觸發後端重新部署。

#### 重新部署前端

```bash
# 提交更改
git add frontend/vite.config.js
git commit -m "fix: Remove hardcoded HMR protocol to support wss:// in production"
git push origin main
```

Zeabur 會自動觸發前端重新部署。

### 步驟 5: 驗證修復

部署完成後，訪問前端網站並檢查：

1. ✅ 開啟瀏覽器開發者工具 (F12)
2. ✅ 前往 Console 標籤
3. ✅ 登入或重新整理頁面
4. ✅ 確認沒有 CORS 錯誤
5. ✅ 確認沒有 WebSocket 混合內容錯誤

預期結果：
- ✅ API 請求成功返回數據
- ✅ 沒有 `Access-Control-Allow-Origin` 錯誤
- ✅ 沒有 `Mixed Content` 錯誤
- ✅ 沒有 `ws://` WebSocket 錯誤

## 技術細節

### CORS 配置

Django 的 CORS 中介軟體 (`django-cors-headers`) 會根據 `CORS_ALLOWED_ORIGINS` 環境變數自動添加正確的 CORS 標頭。不需要在 Nginx 層面重複設定，否則可能導致標頭重複或衝突。

### WebSocket 協議偵測

Vite 會根據頁面的協議（HTTP 或 HTTPS）自動選擇：
- HTTP 頁面 → 使用 `ws://`
- HTTPS 頁面 → 使用 `wss://`

移除硬編碼的 `__HMR_PROTOCOL__` 設定後，Vite 會自動處理。

## 故障排除

### 如果 CORS 錯誤仍然存在

1. 檢查 Zeabur 後端服務的環境變數是否已正確更新
2. 確認後端服務已重新部署
3. 檢查後端日誌，查看 Django 是否正確讀取環境變數：
   ```
   CORS_ALLOWED_ORIGINS: ['https://posefit.zeabur.app', 'https://posefit-project-frontend.zeabur.app']
   ```

### 如果 WebSocket 錯誤仍然存在

1. 清除瀏覽器快取並強制重新整理 (Ctrl + Shift + R)
2. 確認前端已重新部署，且使用最新版本的 `vite.config.js`
3. 檢查瀏覽器 Console，確認沒有來自舊的快取檔案的錯誤

## 相關檔案

- `frontend/vite.config.js` - Vite 配置
- `Dockerfile` - Nginx 和 Django 配置
- `ZEABUR_BACKEND_ENV.txt` - 後端環境變數範本
- `backend/config/settings/production.py` - Django 生產環境設定

## 參考連結

- [Django CORS Headers](https://github.com/adamchainz/django-cors-headers)
- [Vite HMR 配置](https://vitejs.dev/config/server-options.html#server-hmr)
- [Zeabur 環境變數文檔](https://zeabur.com/docs/environment-variables)

