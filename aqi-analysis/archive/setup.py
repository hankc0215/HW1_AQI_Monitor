#!/usr/bin/env python3
"""
環境自動安裝腳本
"""

import subprocess
import sys
import os

def run_command(command, description):
    """執行命令並處理錯誤"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失敗:")
        print(f"錯誤訊息: {e.stderr}")
        return False

def check_python_version():
    """檢查 Python 版本"""
    version = sys.version_info
    print(f"🐍 Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ 需要 Python 3.7 或更高版本")
        return False
    
    return True

def setup_environment():
    """設置環境"""
    print("🚀 開始設置 AQI 監測環境")
    print("=" * 50)
    
    # 檢查 Python 版本
    if not check_python_version():
        return False
    
    # 檢查 pip
    if not run_command("python -m pip --version", "檢查 pip"):
        print("❌ pip 未安裝或有問題")
        return False
    
    # 升級 pip
    run_command("python -m pip install --upgrade pip", "升級 pip")
    
    # 安裝套件
    if not run_command("python -m pip install -r requirements.txt", "安裝所需套件"):
        return False
    
    # 檢查 .env 檔案
    if not os.path.exists('.env'):
        print("⚠️  .env 檔案不存在")
        print("請確保 .env 檔案中包含 EPA_API_KEY")
        return False
    
    # 檢查 API Key
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'EPA_API_KEY=' not in content or 'your_api_key_here' in content:
            print("⚠️  請在 .env 檔案中設定您的 EPA_API_KEY")
            print("如何獲取 API Key:")
            print("1. 前往 https://data.epa.gov.tw/api/v2/")
            print("2. 註冊帳號並申請 API Key")
            print("3. 將 API Key 加入 .env 檔案")
            return False
    
    print("=" * 50)
    print("✅ 環境設置完成！")
    print("現在可以執行: python aqi_monitor.py")
    return True

if __name__ == "__main__":
    if setup_environment():
        # 詢問是否立即執行
        response = input("\n是否立即執行 AQI 監測程式? (y/n): ").lower().strip()
        if response in ['y', 'yes', '是']:
            print("\n🚀 執行 AQI 監測程式...")
            subprocess.run("python aqi_monitor.py", shell=True)
