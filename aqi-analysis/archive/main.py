#!/usr/bin/env python3
"""
台灣即時 AQI 監測系統 - 主程式入口
執行完整的 AQI 數據獲取、地圖生成和資料匯出流程
"""

from aqi_monitor import AQIMonitor

def main():
    """主程式入口"""
    print("=" * 60)
    print("🌍 台灣即時 AQI 監測系統")
    print("=" * 60)
    
    # 創建 AQI 監測器實例
    monitor = AQIMonitor()
    
    # 執行完整流程
    success = monitor.run()
    
    if success:
        print("\n🎉 程式執行成功！")
        print("📁 請查看 outputs/ 目錄中的地圖和 CSV 檔案")
    else:
        print("\n❌ 程式執行失敗，請檢查錯誤訊息")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
