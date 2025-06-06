# 營養健康管理系統 (Nutrition Management System)

## 概述 (Overview)

這是一個全新的營養健康管理系統，整合到 PoseFit 專案中，提供用戶計算基礎代謝率（BMR）和每日消耗總熱量（TDEE），並追蹤體重變化和健康目標進度。

## 主要功能 (Key Features)

### 1. BMR/TDEE 計算器
- **基礎代謝率 (BMR)**: 使用 Mifflin-St Jeor 公式計算
- **每日消耗總熱量 (TDEE)**: BMR × 活動係數
- **即時計算**: 輸入個人資料後立即顯示結果
- **體重管理建議**: 提供維持、減重、增重的熱量建議

### 2. 個人資料管理
- 年齡、性別、身高設定
- 活動量等級選擇（5個等級）
- 健康目標設定（維持/減重/增重）
- 目標體重設定

### 3. 體重記錄追蹤
- 每日體重記錄
- 自動計算當日 BMR/TDEE
- 記錄備註功能
- 歷史記錄管理（編輯/刪除）

### 4. 目標進度追蹤
- 設定體重目標（起始→目標）
- 進度百分比計算
- 時間軸管理
- 合理性評估（每週變化建議）

### 5. 視覺化圖表
- 體重變化趨勢圖
- BMR/TDEE 變化圖表
- 多時間範圍選擇（7天-全部）
- 互動式圖表（Chart.js）

### 6. 儀表板總覽
- 快速統計卡片
- 最近記錄列表
- 目標進度顯示
- 快速操作按鈕

## 技術架構 (Technical Architecture)

### 後端 (Backend)
- **框架**: Django + Django REST Framework
- **資料庫**: MySQL
- **模型**: UserProfile, WeightRecord, GoalProgress
- **API 端點**: RESTful API 設計
- **權限**: JWT 認證保護

### 前端 (Frontend)
- **框架**: Vue 3 + Composition API
- **樣式**: Tailwind CSS
- **圖表**: Chart.js
- **路由**: Vue Router
- **狀態管理**: Reactive refs

## API 端點 (API Endpoints)

```
GET/PUT  /api/nutrition/profile/              # 用戶資料
GET/POST /api/nutrition/weight-records/       # 體重記錄列表
GET/PUT/DELETE /api/nutrition/weight-records/{id}/ # 特定體重記錄
GET/POST /api/nutrition/goals/                # 目標列表
GET/PUT/DELETE /api/nutrition/goals/{id}/     # 特定目標
POST     /api/nutrition/calculate-bmr-tdee/   # BMR/TDEE 計算
GET      /api/nutrition/analytics/            # 分析數據
GET      /api/nutrition/dashboard/            # 儀表板摘要
```

## 資料庫模型 (Database Models)

### UserProfile
- 用戶基本資料（年齡、性別、身高、活動量）
- 健康目標設定
- BMR/TDEE 計算方法

### WeightRecord
- 體重記錄（日期、體重、備註）
- 自動計算的 BMR/TDEE 值
- 與用戶關聯

### GoalProgress
- 目標設定（起始、目標、當前體重）
- 時間軸（開始、目標日期）
- 進度計算屬性

## 使用方式 (Usage)

1. **首次使用**: 訪問 `/nutrition` 頁面，設定個人資料
2. **記錄體重**: 點擊「記錄體重」按鈕，輸入當日體重
3. **設定目標**: 點擊「設定目標」，制定體重目標計劃
4. **查看進度**: 在儀表板查看圖表和統計數據
5. **計算 BMR/TDEE**: 使用計算器工具進行即時計算

## 計算公式 (Calculation Formulas)

### BMR (Mifflin-St Jeor Equation)
- **男性**: BMR = 88.362 + (13.397 × 體重kg) + (4.799 × 身高cm) - (5.677 × 年齡)
- **女性**: BMR = 447.593 + (9.247 × 體重kg) + (3.098 × 身高cm) - (4.330 × 年齡)

### TDEE
- **TDEE = BMR × 活動係數**
- 活動係數：1.2 (久坐) ~ 1.9 (極高活動)

### 體重管理建議
- **維持體重**: TDEE 熱量
- **減重**: TDEE - 385 kcal (每週減 0.5kg)
- **增重**: TDEE + 385 kcal (每週增 0.5kg)

## 安裝與部署 (Installation & Deployment)

### 後端設置
```bash
cd backend
python manage.py makemigrations nutrition
python manage.py migrate nutrition
```

### 前端設置
```bash
cd frontend
npm install  # Chart.js 已包含在 package.json 中
npm run dev
```

## 未來擴展 (Future Enhancements)

1. **營養素追蹤**: 蛋白質、碳水化合物、脂肪攝取記錄
2. **食物資料庫**: 整合食物營養成分資料
3. **運動消耗**: 結合運動記錄計算額外消耗
4. **健康報告**: 生成週期性健康分析報告
5. **社群功能**: 目標分享和互相鼓勵
6. **專家建議**: AI 驅動的個人化建議

## 注意事項 (Notes)

- 所有計算結果僅供參考，不能替代專業醫療建議
- 建議在醫療專業人員指導下制定健康計劃
- 體重變化建議每週不超過 0.5-1kg 為健康範圍
- 系統需要用戶登入才能使用完整功能 