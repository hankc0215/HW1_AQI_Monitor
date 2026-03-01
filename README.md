# 台灣即時 AQI 監測系統

## 專案描述

串接環境部 API 獲取全台即時 AQI 數據，並使用 Folium 在地圖上標示測站位置，包含空間距離計算和資料匯出功能。

## 功能特色

- 🌍 **即時數據獲取**: 串接環境部 API 獲取全台 84 個測站即時 AQI 數據
- 🗺️ **互動式地圖**: 使用 Folium 生成互動式地圖，顯示各測站空氣品質狀況
- 🎨 **三色分類系統**: 綠色(0-50良好)、黃色(51-100普通)、紅色(101+不健康)
- 📏 **空間計算**: 計算每個測站到台北車站的距離
- 📊 **資料匯出**: 將完整資料匯出為 CSV 檔案
- 📈 **統計分析**: 自動生成 AQI 等級分布統計

## 檔案結構

```
HW1/
├── aqi_monitor.py          # 主程式
├── requirements.txt        # 套件依賴
├── setup.py               # 環境安裝腳本
├── test_sample_data.py    # 範例數據測試
├── .env                   # 環境變數設定
├── .gitignore            # Git 忽略檔案
├── README.md             # 專案說明
├── data/                 # 資料目錄
└── outputs/              # 輸出目錄
    ├── aqi_map_*.html    # 互動式地圖
    └── aqi_data_*.csv    # CSV 資料檔案
```

## 安裝與執行

### 1. 環境設定

```bash
# 自動安裝環境
python setup.py

# 或手動安裝
pip install -r requirements.txt
```

### 2. 設定 API Key

在 `.env` 檔案中設定您的環境部 API Key：

```
EPA_API_KEY=your_api_key_here
```

### 3. 執行程式

```bash
# 使用真實 API 數據
python aqi_monitor.py

```

## 輸出檔案

### 地圖檔案
- 檔案位置: `outputs/aqi_map_YYYYMMDD_HHMMSS.html`
- 格式: 互動式 HTML 地圖
- 特色: 可縮放、點擊查看詳細資訊

### CSV 資料檔
- 檔案位置: `outputs/aqi_data_YYYYMMDD_HHMMSS.csv`
- 包含欄位:
  - 測站名稱
  - 縣市
  - AQI 數值
  - 空氣品質等級
  - 主要污染物
  - 緯度、經度
  - 距離台北車站(公里)
  - 狀態
  - 發布時間

## 技術規格

- **Python 版本**: 3.7+
- **主要套件**:
  - `requests`: HTTP 請求
  - `folium`: 地圖視覺化
  - `python-dotenv`: 環境變數管理
- **API 來源**: 環境部開放資料平台
- **座標系統**: WGS84
- **距離計算**: Haversine 公式

## 空間計算

使用 Haversine 公式計算測站到台北車站(25.0478, 121.5170)的直線距離：

```python
distance = 2 * R * arcsin(√(sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)))
```

其中 R = 6371 公里（地球半徑）

## API 資訊

- **端點**: `https://data.moenv.gov.tw/api/v2/AQX_P_432`
- **認證**: API Key
- **格式**: JSON
- **更新頻率**: 每小時

## 開發者資訊

- 開發日期: 2026-03-01
- Python 版本: 3.14
- 最後更新: 即時數據

## 授權

本專案僅供學術研究使用，資料來源為環境部開放資料平台。
