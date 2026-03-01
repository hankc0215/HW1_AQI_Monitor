# Git 和 GitHub 設定說明

由於系統中未安裝 Git 和 GitHub CLI，請手動執行以下步驟：

## 1. 安裝 Git 和 GitHub CLI

### Windows:
```bash
# 下載並安裝 Git
# https://git-scm.com/download/win

# 下載並安裝 GitHub CLI
# https://github.com/cli/cli/releases
```

### 安裝後驗證：
```bash
git --version
gh --version
```

## 2. 設定 Git
```bash
git config --global user.name "你的名字"
git config --global user.email "你的郵件"
```

## 3. 登入 GitHub
```bash
gh auth login
```

## 4. 初始化倉庫並推送
```bash
# 在專案目錄中執行
git init
git add .
git commit -m "Initial commit: AQI monitoring system"

# 建立 GitHub 倉庫
gh repo create aqi-analysis --public --source=. --remote=origin --push

# 或者手動推送
git branch -M main
git remote add origin https://github.com/你的用戶名/aqi-analysis.git
git push -u origin main
```

## 5. 驗證
訪問 https://github.com/你的用戶名/aqi-analysis 查看已推送的程式碼

---

## 專案已準備就緒的內容

✅ **空間計算功能**: 使用 Haversine 公式計算各測站到台北車站的距離
✅ **CSV 資料匯出**: 完整的測站資料包含距離計算結果
✅ **互動式地圖**: 優化的三色分類 AQI 地圖
✅ **README 文件**: 完整的專案說明文件

## 輸出檔案範例

- **地圖**: `outputs/aqi_map_20260301_140807.html`
- **資料**: `outputs/aqi_data_20260301_140807.csv`

CSV 檔案包含 84 個測站的完整資訊，包括：
- 測站名稱、縣市、AQI 數值
- 空氣品質等級、主要污染物
- 精確座標和到台北車站的距離
- 即時狀態和發布時間
