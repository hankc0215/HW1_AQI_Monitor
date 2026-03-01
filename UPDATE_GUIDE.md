# 專案更新指南

## 🔄 如何更新專案到 GitHub

### 1. 檢查變更狀態
```bash
"C:\Program Files\Git\bin\git.exe" status
```

### 2. 添加修改的檔案
```bash
"C:\Program Files\Git\bin\git.exe" add .
```

### 3. 提交變更（使用清晰的 Commit Message）
```bash
# 功能更新
"C:\Program Files\Git\bin\git.exe" commit -m "feat: 描述你的功能更新"

# 錯誤修正
"C:\Program Files\Git\bin\git.exe" commit -m "fix: 描述修正的問題"

# 文檔更新
"C:\Program Files\Git\bin\git.exe" commit -m "docs: 更新文檔內容"

# 程式碼重構
"C:\Program Files\Git\bin\git.exe" commit -m "refactor: 重構程式碼結構"
```

### 4. 推送到 GitHub
```bash
"C:\Program Files\Git\bin\git.exe" push origin main
```

## 📝 Commit Message 最佳實踐

### 格式：`<類型>: <簡短描述>`

**類型選項：**
- `feat`: 新功能
- `fix`: 錯誤修正
- `docs`: 文檔更新
- `style`: 程式碼格式調整
- `refactor`: 程式碼重構
- `test`: 測試相關
- `chore`: 建置過程或輔助工具變更

**範例：**
```bash
feat: 新增測站距離排序功能
fix: 修正 CSV 匯出時的編碼問題
docs: 更新 README 安裝說明
refactor: 優化 API 請求錯誤處理
```

## 🚀 快速更新腳本

如果你經常更新，可以建立批次檔：

### Windows (update.bat)
```batch
@echo off
echo 正在更新專案...
echo.

echo 1. 檢查狀態...
"C:\Program Files\Git\bin\git.exe" status

echo.
echo 2. 添加所有變更...
"C:\Program Files\Git\bin\git.exe" add .

echo.
echo 3. 請輸入 Commit Message:
set /p message=
"C:\Program Files\Git\bin\git.exe" commit -m "%message%"

echo.
echo 4. 推送到 GitHub...
"C:\Program Files\Git\bin\git.exe" push origin main

echo.
echo ✅ 更新完成！
pause
```

## 🔍 常見問題

### Q: 如何查看提交歷史？
```bash
"C:\Program Files\Git\bin\git.exe" log --oneline -10
```

### Q: 如何回滾到上一個版本？
```bash
"C:\Program Files\Git\bin\git.exe" reset --hard HEAD~1
```

### Q: 如何查看遠端狀態？
```bash
"C:\Program Files\Git\bin\git.exe" remote -v
```

### Q: 如何同步遠端變更？
```bash
"C:\Program Files\Git\bin\git.exe" pull origin main
```

## 📱 GitHub CLI 快速操作

### 查看倉庫狀態
```bash
"C:\Program Files\GitHub CLI\gh.exe" repo view hankc0215/HW1_AQI_Monitor
```

### 查看最近的 Issues
```bash
"C:\Program Files\GitHub CLI\gh.exe" issue list --repo hankc0215/HW1_AQI_Monitor
```

### 創建 Release
```bash
"C:\Program Files\GitHub CLI\gh.exe" release create v1.0.0 --title "版本 1.0.0" --notes "初始版本發布"
```

---

**記住：** 每次更新前先 `pull` 確保本地版本最新，避免衝突！
