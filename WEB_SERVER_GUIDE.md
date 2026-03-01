# AQI 監測網站使用指南

## 🌐 動態地圖網站

現在你有了一個真正的動態網站，而不是靜態快照！

### 🚀 啟動網站

```bash
# 啟動網站伺服器
python web_server.py

# 或使用完整路徑
$env:PYTHONIOENCODING="utf-8"; python web_server.py
```

### 📱 訪問方式

1. **本地訪問**: http://localhost:5000
2. **網路訪問**: http://你的IP:5000 (區域網路內其他設備可訪問)

### ✨ 主要特色

#### 🔄 **即時更新**
- 重新整理頁面即可獲取最新數據
- 每 5 分鐘自動重新整理
- 手動重新整理按鈕

#### 🗺️ **互動式地圖**
- 使用 Leaflet.js (輕量級地圖庫)
- 點擊測站查看詳細資訊
- 懸停顯示快速資訊

#### 📊 **即時統計**
- 右側資訊面板顯示統計數據
- 顯示各等級測站數量
- 最後更新時間

#### 🎨 **三色分類系統**
- 🟢 綠色 (0-50): 良好
- 🟡 黃色 (51-100): 普通  
- 🔴 紅色 (101+): 不健康

### 🛠️ 技術架構

#### **後端 (Flask)**
- Python Flask 輕量級網頁框架
- RESTful API 端點: `/api/aqi-data`
- 即時從環境部 API 獲取數據
- 距離計算和數據處理

#### **前端 (HTML/JavaScript)**
- Leaflet.js 地圖庫
- 原生 JavaScript (無需複雜框架)
- 響應式設計
- 自動重新整理機制

### 📁 檔案結構

```
HW1_AQI_Monitor/
├── web_server.py          # 🆕 網站伺服器主程式
├── aqi_monitor.py         # 原始監測程式
├── main.py               # 原始主程式入口
├── requirements.txt       # 🔄 新增 flask 依賴
└── outputs/              # 靜態輸出檔案
```

### 🔄 更新流程

#### **開發模式**
```bash
# 1. 修改 web_server.py
# 2. 伺服器會自動重新整理 (debug=True)
# 3. 重新整理瀏覽器查看變更
```

#### **生產模式**
```bash
# 停用 debug 模式
app.run(debug=False, host='0.0.0.0', port=5000)
```

### 🌍 網路部署

#### **區域網路訪問**
```bash
# 其他設備可透過你的 IP 訪問
http://192.168.1.100:5000  # 範例 IP
```

#### **雲端部署選項**
1. **Heroku**: 免費層級支援 Flask
2. **PythonAnywhere**: 專為 Python 設計
3. **VPS**: 完全控制權

### 📊 API 端點

#### **數據端點**
```
GET /api/aqi-data
```

**回應格式 (JSON):**
```json
[
  {
    "sitename": "台北",
    "county": "臺北市", 
    "aqi": "45",
    "level": "良好",
    "pollutant": "",
    "latitude": 25.0478,
    "longitude": 121.5170,
    "distance": 0.0,
    "color": "#00E400",
    "publishtime": "2026/03/01 15:00:00",
    "status": "良好"
  }
]
```

### 🔧 自訂功能

#### **修改重新整理間隔**
```javascript
// 每 5 分鐘自動重新整理
setInterval(refreshData, 5 * 60 * 1000);

// 改為每 2 分鐘
setInterval(refreshData, 2 * 60 * 1000);
```

#### **修改地圖中心點**
```javascript
// 台灣中心
map.setView([23.8, 121.0], 7);

// 台北中心
map.setView([25.0478, 121.5170], 10);
```

#### **新增更多統計資訊**
```javascript
// 在 updateStats 函數中新增
const avgAQI = Math.round(data.reduce((sum, s) => sum + parseInt(s.aqi || 0), 0) / data.length);
document.getElementById('avgAQI').textContent = avgAQI;
```

### 🚀 優勢對比

| 功能 | 靜態快照系統 | 動態網站系統 |
|------|-------------|-------------|
| 數據更新 | 手動重新執行 | 重新整理頁面 |
| 互動性 | 靜態 HTML | 完全互動 |
| 部署方式 | 檔案分享 | 網站服務 |
| 即時性 | 延遲較高 | 即時更新 |
| 使用體驗 | 需要下載 | 直接瀏覽 |

### 💡 使用建議

1. **開發測試**: 使用 `python web_server.py`
2. **分享展示**: 直接分享 URL 即可
3. **長期運行**: 建議部署到雲端平台
4. **效能優化**: 可考慮加入數據快取

---

**🎉 現在你有了一個真正的動態 AQI 監測網站！**

重新整理頁面即可看到最新的空氣品質數據！
