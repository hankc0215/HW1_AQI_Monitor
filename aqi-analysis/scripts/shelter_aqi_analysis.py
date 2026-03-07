#!/usr/bin/env python3
"""
重新執行最終清理後資料的最近測站分析
使用最終清理後的避難所資料重新進行 AQI 風險分析
"""

import os
import json
import requests
import pandas as pd
import math
from dotenv import load_dotenv
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 載入環境變數
load_dotenv(encoding='utf-8')

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    計算兩點間距離（公里）
    使用 Haversine 公式
    """
    # 轉換為弧度
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine 公式
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # 地球半徑（公里）
    r = 6371
    distance = r * c
    
    return round(distance, 2)

def fetch_aqi_data():
    """獲取即時 AQI 數據"""
    api_key = os.getenv('EPA_API_KEY', '5a37aebe-f3cb-4aeb-bdae-fd285e2808e2')
    url = 'https://data.moenv.gov.tw/api/v2/AQX_P_432'
    params = {
        'api_key': api_key,
        'limit': '1000',
        'sort': 'ImportDate desc',
        'format': 'json'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30, verify=False)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'records' in data:
            return data['records']
        else:
            return []
    except Exception as e:
        print(f"獲取 AQI 數據失敗: {e}")
        return []

def scenario_injection(aqi_data):
    """
    情境注入：模擬高污染 AQI=150
    選擇特定測站並覆蓋其 AQI 值
    """
    print("=== 情境注入模擬 ===")
    
    # 檢查當前 AQI 狀態
    all_good = True
    for station in aqi_data:
        try:
            aqi = int(float(station.get('aqi', 0))) if station.get('aqi') else 0
            if aqi >= 50:
                all_good = False
                break
        except (ValueError, TypeError):
            continue
    
    # 強制執行情境注入以驗證邏輯
    all_good = True
    
    if all_good:
        print("執行情境注入以驗證分析邏輯...")
        
        # 選擇高雄測站進行注入
        target_station = None
        for station in aqi_data:
            if '高雄' in station.get('county', '') or 'Kaohsiung' in station.get('county', ''):
                target_station = station
                break
        
        if not target_station:
            # 如果找不到高雄，選擇第一個測站
            target_station = aqi_data[0]
        
        # 注入 AQI=150
        original_aqi = target_station.get('aqi', '0')
        target_station['aqi'] = '150'
        target_station['status'] = '不健康'
        
        print(f"情境注入: {target_station.get('sitename', 'Unknown')} AQI 從 {original_aqi} -> 150")
        print(f"地點: {target_station.get('county', 'Unknown')}")
        
        return True, target_station
    else:
        print("當前已有 AQI >= 50 的測站，無需情境注入")
        return False, None

def load_final_cleaned_shelter_data():
    """讀取最終清理後的避難收容處所資料"""
    filepath = 'outputs/shelter_shelters_final_cleaned.csv'
    
    try:
        df = pd.read_csv(filepath, encoding='utf-8-sig')
        print(f"載入 {len(df)} 筆最終清理後的避難收容處所資料")
        return df
    except Exception as e:
        print(f"讀取最終清理後避難所資料失敗: {e}")
        return pd.DataFrame()

def find_nearest_aqi_station(shelter_lat, shelter_lon, aqi_data):
    """
    找出避難所最近的 AQI 測站
    """
    min_distance = float('inf')
    nearest_station = None
    
    for station in aqi_data:
        try:
            station_lat = float(station.get('latitude', 0))
            station_lon = float(station.get('longitude', 0))
            
            if station_lat == 0 or station_lon == 0:
                continue
            
            distance = haversine_distance(shelter_lat, shelter_lon, station_lat, station_lon)
            
            if distance < min_distance:
                min_distance = distance
                nearest_station = station
                
        except (ValueError, TypeError):
            continue
    
    return nearest_station, min_distance

def analyze_final_cleaned_shelter_aqi():
    """分析最終清理後避難所與最近 AQI 測站"""
    print("="*70)
    print("最終清理後避難所最近測站分析與風險評估")
    print("="*70)
    
    # 獲取資料
    aqi_data = fetch_aqi_data()
    shelter_df = load_final_cleaned_shelter_data()
    
    if not aqi_data or shelter_df.empty:
        print("無法獲取必要資料")
        return None
    
    print(f"AQI 測站數量: {len(aqi_data)}")
    print(f"最終清理後避難收容處所數量: {len(shelter_df)}")
    
    # 情境注入
    injection_applied, injected_station = scenario_injection(aqi_data)
    
    # 分析結果
    results = []
    risk_stats = {'high_risk': 0, 'warning': 0, 'safe': 0}
    
    print("\n開始分析最終清理後避難所...")
    
    for idx, row in shelter_df.iterrows():
        try:
            # 取得避難所資料
            shelter_id = row.iloc[0]
            shelter_name = row.iloc[6]
            shelter_county = row.iloc[1]
            shelter_lat = float(row.iloc[5])
            shelter_lon = float(row.iloc[4])
            is_indoor = row['is_indoor']
            capacity = row.iloc[8]
            
            if shelter_lat == 0 or shelter_lon == 0:
                continue
            
            # 找出最近 AQI 測站
            nearest_station, distance = find_nearest_aqi_station(shelter_lat, shelter_lon, aqi_data)
            
            if not nearest_station:
                continue
            
            # 取得 AQI 資料
            station_name = nearest_station.get('sitename', 'Unknown')
            station_county = nearest_station.get('county', '')
            aqi_value = nearest_station.get('aqi', '')
            status = nearest_station.get('status', '')
            pollutant = nearest_station.get('pollutant', '')
            
            # 風險標籤
            risk_label = 'Safe'
            try:
                aqi_num = int(float(aqi_value)) if aqi_value else 0
            except (ValueError, TypeError):
                aqi_num = 0
            
            if aqi_num > 100:
                risk_label = 'High Risk'
                risk_stats['high_risk'] += 1
            elif aqi_num > 50 and not is_indoor:  # 室外且 AQI > 50
                risk_label = 'Warning'
                risk_stats['warning'] += 1
            else:
                risk_stats['safe'] += 1
            
            # 記錄結果
            result = {
                'shelter_id': shelter_id,
                'shelter_name': shelter_name,
                'shelter_county': shelter_county,
                'shelter_lat': shelter_lat,
                'shelter_lon': shelter_lon,
                'is_indoor': is_indoor,
                'capacity': capacity,
                'nearest_station': station_name,
                'station_county': station_county,
                'distance_km': distance,
                'aqi_value': aqi_value,
                'aqi_status': status,
                'pollutant': pollutant,
                'risk_label': risk_label,
                'data_source': 'final_cleaned'  # 標記為最終清理後資料
            }
            
            results.append(result)
            
        except Exception as e:
            print(f"處理避難所 {idx} 時發生錯誤: {e}")
            continue
    
    # 轉換為 DataFrame
    results_df = pd.DataFrame(results)
    
    # 輸出統計
    print(f"\n最終清理後分析完成!")
    print(f"成功分析: {len(results_df)} 個避難所")
    print(f"風險分布:")
    print(f"  High Risk (AQI > 100): {risk_stats['high_risk']}")
    print(f"  Warning (AQI > 50 + 室外): {risk_stats['warning']}")
    print(f"  Safe: {risk_stats['safe']}")
    
    # 顯示 High Risk 範例
    high_risk_df = results_df[results_df['risk_label'] == 'High Risk']
    if len(high_risk_df) > 0:
        print(f"\nHigh Risk 避難所範例 (前5筆):")
        for _, row in high_risk_df.head(5).iterrows():
            print(f"  {row['shelter_name']} ({row['shelter_county']}) - AQI: {row['aqi_value']}, 距離: {row['distance_km']}km")
    
    # 顯示 Warning 範例
    warning_df = results_df[results_df['risk_label'] == 'Warning']
    if len(warning_df) > 0:
        print(f"\nWarning 避難所範例 (前5筆):")
        for _, row in warning_df.head(5).iterrows():
            print(f"  {row['shelter_name']} ({row['shelter_county']}) - 室外, AQI: {row['aqi_value']}, 距離: {row['distance_km']}km")
    
    # 保存結果
    output_path = 'outputs/shelter_aqi_analysis_final.csv'
    results_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n最終清理後分析結果已儲存至: {output_path}")
    
    # 驗證情境注入效果
    if injection_applied and injected_station:
        affected_shelters = results_df[results_df['nearest_station'] == injected_station.get('sitename', '')]
        print(f"\n情境注入影響: {len(affected_shelters)} 個最終清理後避難所受到 {injected_station.get('sitename')} 測站影響")
        
        high_risk_affected = affected_shelters[affected_shelters['risk_label'] == 'High Risk']
        if len(high_risk_affected) > 0:
            print(f"其中 {len(high_risk_affected)} 個被標記為 High Risk")
    
    return results_df

if __name__ == "__main__":
    analyze_final_cleaned_shelter_aqi()
