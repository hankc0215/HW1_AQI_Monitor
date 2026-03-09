#!/usr/bin/env python3
"""
台灣即時 AQI 監測系統
串接環境部 API 獲取全台即時 AQI 數據，並使用 Folium 在地圖上標示測站位置
"""

import os
import requests
import folium
from dotenv import load_dotenv
from datetime import datetime
import json
import urllib3
import math
import csv

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 載入環境變數
load_dotenv(encoding='utf-8')

class AQIMonitor:
    def __init__(self):
        # 從環境變數讀取設定
        self.api_key = os.getenv('EPA_API_KEY', '')
        self.base_url = "https://airquality.epa.gov.tw/api/v2"
        self.aqi_data = None
        
        # 從環境變數讀取台北車站座標
        taipei_lat = float(os.getenv('TAIPEI_STATION_LAT', '25.0478'))
        taipei_lon = float(os.getenv('TAIPEI_STATION_LON', '121.5170'))
        self.taipei_station = (taipei_lat, taipei_lon)
        
        # CRS 設定
        self.default_crs = os.getenv('DEFAULT_CRS', 'EPSG:4326')
        self.taiwan_crs = os.getenv('TAIWAN_CRS', 'EPSG:3826')
        self.output_crs = os.getenv('OUTPUT_CRS', 'EPSG:4326')
        
        if not self.api_key or self.api_key == 'your_api_key_here':
            print(f"DEBUG: API Key = '{self.api_key}'")
            print("WARNING: 請在 .env 檔案中設定 EPA_API_KEY")
            print("   範例: EPA_API_KEY=your_api_key_here")
            exit(1)
    
    def fetch_aqi_data(self):
        """獲取全台即時 AQI 數據"""
        # 使用環境部正確的 API URL
        url = "https://data.moenv.gov.tw/api/v2/AQX_P_432"
        params = {
            "api_key": self.api_key,
            "limit": "1000",
            "sort": "ImportDate desc",
            "format": "json"
        }
        
        try:
            print("正在獲取 AQI 數據...")
            # 禁用 SSL 驗證以解決憑證問題
            response = requests.get(url, params=params, timeout=30, verify=False)
            response.raise_for_status()
            
            data = response.json()
            
            # 檢查 API 回應結構
            print(f"API 回應類型: {type(data)}")
            if isinstance(data, list) and len(data) > 0:
                print(f"第一筆資料範例: {data[0]}")
            
            # 檢查可能的資料結構
            if isinstance(data, list):
                self.aqi_data = data
                print(f"成功獲取 {len(self.aqi_data)} 個測站數據 (直接列表)")
                return True
            elif isinstance(data, dict):
                if 'records' in data:
                    self.aqi_data = data['records']
                    print(f"成功獲取 {len(self.aqi_data)} 個測站數據 (records)")
                    return True
                elif 'data' in data:
                    self.aqi_data = data['data']
                    print(f"成功獲取 {len(self.aqi_data)} 個測站數據 (data)")
                    return True
                else:
                    print("API 回應格式錯誤 - 找不到資料欄位")
                    print(f"可用鍵值: {list(data.keys())}")
                    return False
            else:
                print("API 回應格式錯誤 - 非字典或列表")
                return False
            
        except requests.exceptions.RequestException as e:
            print(f"API 請求失敗: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"JSON 解析失敗: {e}")
            return False
    
    def get_aqi_color(self, aqi_value):
        """根據 AQI 值返回對應顏色 - 簡化三色分類"""
        try:
            aqi = int(aqi_value)
        except (ValueError, TypeError):
            return '#808080'  # 灰色 (無效數據)
        
        if aqi <= 50:
            return '#00E400'  # 綠色 (良好)
        elif aqi <= 100:
            return '#FFFF00'  # 黃色 (普通)
        else:
            return '#FF0000'  # 紅色 (不健康)
    
    def get_aqi_level(self, aqi_value):
        """根據 AQI 值返回等級描述 - 簡化三色分類"""
        try:
            aqi = int(aqi_value)
        except (ValueError, TypeError):
            return '無數據'
        
        if aqi <= 50:
            return '良好'
        elif aqi <= 100:
            return '普通'
        else:
            return '不健康'
    
    def calculate_distance_to_taipei(self, lat, lon):
        """計算測站到台北車站的距離（公里）"""
        # 使用 Haversine 公式計算兩點間距離
        lat1, lon1 = math.radians(lat), math.radians(lon)
        lat2, lon2 = math.radians(self.taipei_station[0]), math.radians(self.taipei_station[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # 地球半徑（公里）
        r = 6371
        
        distance = r * c
        return round(distance, 2)
    
    def export_to_csv(self):
        """將測站資料和距離計算結果匯出至 CSV"""
        if not self.aqi_data:
            print("沒有資料可匯出")
            return False
        
        filename = f"outputs/aqi_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = [
                    '測站名稱', '縣市', 'AQI', '空氣品質等級', '主要污染物', 
                    '緯度', '經度', '距離台北車站(公里)', '狀態', '發布時間'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # 寫入標題
                writer.writeheader()
                
                # 寫入資料
                for station in self.aqi_data:
                    try:
                        site_name = station.get('sitename', '未知測站')
                        county = station.get('county', '未知縣市')
                        aqi = station.get('aqi', '')
                        pollutant = station.get('pollutant', '')
                        status = station.get('status', '')
                        publishtime = station.get('publishtime', '')
                        lat = float(station.get('latitude', 0))
                        lon = float(station.get('longitude', 0))
                        
                        # 計算距離
                        distance = self.calculate_distance_to_taipei(lat, lon) if lat != 0 and lon != 0 else '無效座標'
                        
                        # 獲取等級
                        level = self.get_aqi_level(aqi)
                        
                        writer.writerow({
                            '測站名稱': site_name,
                            '縣市': county,
                            'AQI': aqi,
                            '空氣品質等級': level,
                            '主要污染物': pollutant,
                            '緯度': lat,
                            '經度': lon,
                            '距離台北車站(公里)': distance,
                            '狀態': status,
                            '發布時間': publishtime
                        })
                        
                    except (ValueError, KeyError) as e:
                        print(f"跳過無效測站資料: {e}")
                        continue
            
            print(f"資料已匯出至: {filename}")
            return True
            
        except Exception as e:
            print(f"匯出 CSV 失敗: {e}")
            return False
    
    def create_map(self):
        """創建 AQI 地圖"""
        if not self.aqi_data:
            print("沒有 AQI 數據，請先獲取數據")
            return None
        
        # 台灣中心點
        taiwan_center = [23.8, 121.0]
        
        # 創建地圖
        m = folium.Map(
            location=taiwan_center,
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        print("正在生成地圖...")
        
        # 添加測站標記
        for station in self.aqi_data:
            try:
                # 獲取測站資訊
                site_name = station.get('sitename', '未知測站')
                county = station.get('county', '未知縣市')
                aqi = station.get('aqi', '')
                pollutant = station.get('pollutant', '')
                status = station.get('status', '')
                
                # 獲取座標
                lat = float(station.get('latitude', 0))
                lon = float(station.get('longitude', 0))
                
                if lat == 0 or lon == 0:
                    continue
                
                # 獲取顏色和等級
                color = self.get_aqi_color(aqi)
                level = self.get_aqi_level(aqi)
                
                # 創建簡化的彈出窗口內容
                popup_content = f"""
                <div style="font-family: Arial, sans-serif; min-width: 200px;">
                    <h4 style="margin: 0 0 10px 0; color: #333;">{site_name} 測站</h4>
                    <p style="margin: 5px 0;"><strong>所在地:</strong> {county}</p>
                    <p style="margin: 5px 0;"><strong>即時 AQI:</strong> <span style="font-size: 18px; font-weight: bold; color: {color};">{aqi}</span></p>
                    <p style="margin: 5px 0;"><strong>空氣品質:</strong> {level}</p>
                    {f'<p style="margin: 5px 0;"><strong>主要污染物:</strong> {pollutant}</p>' if pollutant else ''}
                </div>
                """
                
                # 創建圓形標記
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=8,
                    popup=folium.Popup(popup_content, max_width=300),
                    color='black',
                    weight=1,
                    fillColor=color,
                    fillOpacity=0.8,
                    tooltip=f"{site_name}: AQI {aqi}"
                ).add_to(m)
                
            except (ValueError, KeyError) as e:
                print(f"跳過無效測站數據: {e}")
                continue
        
        # 添加簡化的圖例
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 180px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
        <h4 style="margin: 0 0 10px 0; text-align: center;">AQI 等級圖例</h4>
        <p style="margin: 5px 0;"><span style="display: inline-block; width: 12px; height: 12px; background-color: #00E400; border-radius: 50%; margin-right: 8px;"></span>0-50 良好</p>
        <p style="margin: 5px 0;"><span style="display: inline-block; width: 12px; height: 12px; background-color: #FFFF00; border-radius: 50%; margin-right: 8px;"></span>51-100 普通</p>
        <p style="margin: 5px 0;"><span style="display: inline-block; width: 12px; height: 12px; background-color: #FF0000; border-radius: 50%; margin-right: 8px;"></span>101+ 不健康</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
    
    def save_map(self, map_obj, filename=None):
        """保存地圖到文件"""
        if not map_obj:
            print("沒有地圖對象")
            return False
        
        if filename is None:
            filename = f"outputs/aqi_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        try:
            map_obj.save(filename)
            print(f"地圖已保存至: {filename}")
            return True
        except Exception as e:
            print(f"保存地圖失敗: {e}")
            return False
    
    def run(self):
        """執行完整流程"""
        print("台灣即時 AQI 監測系統啟動")
        print("=" * 50)
        
        # 獲取數據
        if not self.fetch_aqi_data():
            return False
        
        # 創建地圖
        aqi_map = self.create_map()
        if not aqi_map:
            return False
        
        # 保存地圖
        self.save_map(aqi_map)
        
        # 匯出 CSV 資料
        self.export_to_csv()
        
        # 顯示統計資訊
        self.show_statistics()
        
        print("=" * 50)
        print("AQI 監測完成！")
        return True
    
    def show_statistics(self):
        """顯示統計資訊"""
        if not self.aqi_data:
            return
        
        print("\n統計資訊:")
        print(f"總測站數: {len(self.aqi_data)}")
        
        # 統計各等級數量
        level_counts = {}
        for station in self.aqi_data:
            aqi = station.get('aqi', '')
            level = self.get_aqi_level(aqi)
            level_counts[level] = level_counts.get(level, 0) + 1
        
        print("AQI 等級分布:")
        for level, count in sorted(level_counts.items()):
            print(f"  {level}: {count} 個測站")

if __name__ == "__main__":
    monitor = AQIMonitor()
    monitor.run()
