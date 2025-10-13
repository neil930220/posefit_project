# 前端環境變數設定說明

## 生產環境部署到 Zeabur

### 方式一：在 Zeabur 直接設定環境變數（推薦）

在 Zeabur 前端服務的「環境變數」頁面新增：

```
VITE_API_BASE_URL=https://your-backend-service.zeabur.app/api/
```

⚠️ **注意：**
- 請將 `your-backend-service` 替換為您實際的後端服務域名
- 結尾必須包含 `/api/`
- 必須使用 `https://`

### 方式二：建立 .env.production 檔案

如果您想在本地建置，請建立 `frontend/.env.production` 檔案：

```bash
# 在 frontend 目錄下建立檔案
touch .env.production
```

檔案內容：
```
VITE_API_BASE_URL=https://your-backend-service.zeabur.app/api/
```

---

## 設定完成檢查

1. ✅ 確認 URL 格式正確（包含 https:// 和 /api/）
2. ✅ 確認後端服務已成功部署
3. ✅ 測試前端是否能成功呼叫後端 API

---

## 疑難排解

### 問題：前端無法連接後端

**檢查清單：**
- [ ] `VITE_API_BASE_URL` 是否設定正確
- [ ] 後端 `CORS_ALLOWED_ORIGINS` 是否包含前端域名
- [ ] 後端 `ALLOWED_HOSTS` 是否包含後端域名
- [ ] 前端和後端都使用 HTTPS

### 問題：環境變數未生效

**解決方式：**
- Vite 的環境變數必須以 `VITE_` 開頭
- 修改環境變數後需要重新建置：`npm run build`
- 在 Zeabur 上修改環境變數後需要重新部署服務

