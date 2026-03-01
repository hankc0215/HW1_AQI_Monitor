# 🌍 台灣即時 AQI 監測系統

## 📱 **線上體驗**

**🌐 立即訪問**: https://hankc0215.github.io/HW1_AQI_Monitor/

---

## 🎯 專案概述

串接環境部 API 獲取全台即時 AQI 數據，開發互動式地圖網站，包含空間距離計算和即時數據更新功能。

### ✨ 核心功能

- 🌍 **即時數據獲取**: 串接環境部 API 獲取全台 84 個測站即時 AQI 數據
- 🗺️ **互動式地圖**: 使用 Leaflet.js 開發動態地圖，支援縮放、點擊查看詳細資訊
- 🔄 **即時更新**: 重新整理頁面即可獲取最新數據，每 5 分鐘自動更新
- 🎨 **三色分類系統**: 綠色(0-50良好)、黃色(51-100普通)、紅色(101+不健康)
- 📏 **空間計算**: 使用 Haversine 公式計算每個測站到台北車站的距離
- 📊 **統計分析**: 即時顯示各等級測站分布和平均 AQI
- 📥 **資料匯出**: 一鍵匯出完整測站資料為 CSV 檔案

---

## 🚀 快速開始

### 🌐 **線上體驗** (推薦)
直接訪問: https://hankc0215.github.io/HW1_AQI_Monitor/

### 💻 **本地執行**
```bash
# 1. 克隆專案
git clone https://github.com/hankc0215/HW1_AQI_Monitor
cd HW1_AQI_Monitor

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 啟動網站
python web_server.py

# 4. 訪問
http://localhost:5000
```

### 📊 **靜態分析**
```bash
# 生成靜態地圖和 CSV
python aqi_monitor.py

# 或使用主程式
python main.py
```

---

## 📁 專案結構

```
HW1_AQI_Monitor/
├── web_server.py          # 🌐 Flask 動態網站伺服器
├── aqi_monitor.py         # 📊 核心監測程式
├── main.py               # 🚀 主程式入口
├── deploy_github_pages.py # 🚀 GitHub Pages 部署腳本
├── requirements.txt       # 📦 套件依賴
├── setup.py              # ⚙️ 環境安裝腳本
├── .env                  # 🔐 環境變數設定
├── .gitignore           # 🚫 Git 忽略規則
├── docs/                 # 📁 GitHub Pages 靜態檔案
│   └── index.html        # 🌐 靜態網站
├── data/                 # 📁 資料目錄
└── outputs/              # 📁 輸出目錄
    ├── aqi_map_*.html    # 🗺️ 靜態地圖檔案
    └── aqi_data_*.csv    # 📊 CSV 資料檔案
```

---

## 🛠️ 技術規格

### **後端技術**
- **Python 3.7+**: 主要開發語言
- **Flask**: 輕量級網頁框架
- **Requests**: HTTP 請求處理
- **Python-dotenv**: 環境變數管理

### **前端技術**
- **HTML5 + CSS3**: 現代網頁標準
- **JavaScript ES6+**: 前端邏輯處理
- **Leaflet.js**: 開源地圖庫
- **OpenStreetMap**: 地圖資料來源

### **數據處理**
- **環境部 API**: 即時 AQI 數據來源
- **Haversine 公式**: 地理距離計算
- **JSON**: 數據交換格式
- **CSV**: 資料匯出格式

---

## 🎨 功能特色

### **互動式地圖**
- 🗺️ 全台 84 個測站即時顯示
- 🎯 點擊測站查看詳細資訊
- 📍 懸停顯示快速資訊
- 🔍 支援縮放和平移操作

### **即時統計面板**
- 📊 總測站數量統計
- 📈 平均 AQI 計算
- 🎨 各等級分布顯示
- ⏰ 最後更新時間

### **資料匯出功能**
- 📥 一鍵匯出 CSV 檔案
- 📋 包含完整測站資訊
- 📏 距離計算結果
- 🕐 即時數據時間戳

---

## 📱 使用說明

### **網站操作**
1. **載入地圖**: 自動載入全台測站數據
2. **查看資訊**: 點擊圓點查看測站詳細資訊
3. **重新整理**: 點擊重新整理按鈕獲取最新數據
4. **匯出資料**: 點擊匯出按鈕下載 CSV 檔案

### **AQI 等級說明**
| 顏色 | AQI 範圍 | 等級 | 健康建議 |
|------|----------|------|----------|
| 🟢 綠色 | 0-50 | 良好 | 空氣品質令人滿意 |
| 🟡 黃色 | 51-100 | 普通 | 空氣品質可接受 |
| 🔴 紅色 | 101+ | 不健康 | 敏感族群應減少戶外活動 |

---

## 🚀 部署方式

### **GitHub Pages** (已部署)
- **網址**: https://hankc0215.github.io/HW1_AQI_Monitor/
- **特色**: 免費、全球 CDN、自動部署
- **更新**: 推送程式碼自動更新

### **本地伺服器**
```bash
python web_server.py
# 訪問: http://localhost:5000
```

### **雲端平台**
- **Heroku**: 支援 Flask 應用
- **PythonAnywhere**: Python 專用平台
- **VPS**: 完全控制權

---

## 📊 API 資訊

### **環境部 API**
- **端點**: `https://data.moenv.gov.tw/api/v2/AQX_P_432`
- **認證**: API Key
- **格式**: JSON
- **更新頻率**: 每小時

### **本地 API 端點**
- **數據端點**: `GET /api/aqi-data`
- **回應格式**: JSON
- **內容**: 處理後的測站資料

---

## 🔧 開發指南

### **環境設定**
```bash
# 設定 API Key
echo "EPA_API_KEY=your_api_key_here" > .env

# 安裝依賴
pip install -r requirements.txt
```

### **自訂功能**
- **修改更新頻率**: 調整 JavaScript 中的 `setInterval`
- **更改地圖中心**: 修改 `map.setView()` 參數
- **新增統計資訊**: 在 `updateStats()` 函數中添加

---

## 📈 專案亮點

### **技術實作**
- ✅ API 數據串接與處理
- ✅ 空間距離計算 (Haversine 公式)
- ✅ 互動式地圖開發
- ✅ 響應式網頁設計
- ✅ 即時數據更新機制
- ✅ 多種部署方案

### **創新特色**
- 🌍 全台 84 個測站即時監測
- 📏 到台北車站的精確距離計算
- 🎨 直觀的三色分類視覺化
- 📱 手機、平板、電腦全支援
- 🌐 全球可訪問的 GitHub Pages 部署

---

## 📞 聯絡資訊

- **GitHub**: https://github.com/hankc0215/HW1_AQI_Monitor
- **線上體驗**: https://hankc0215.github.io/HW1_AQI_Monitor/

---

## 📄 授權

本專案僅供學術研究使用，資料來源為環境部開放資料平台。

---

**🌟 立即體驗完整的台灣 AQI 監測系統！**

**https://hankc0215.github.io/HW1_AQI_Monitor/**
