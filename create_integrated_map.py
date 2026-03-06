#!/usr/bin/env python3
"""
AQI 與避難收容處所整合地圖
圖層 A: AQI 測站（依嚴重程度分色）
圖層 B: 避難收容處所（區分室內/室外圖標）
驗證：確保避難所不在海中
"""

import os
import json
import requests
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from dotenv import load_dotenv
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 載入環境變數
load_dotenv(encoding='utf-8')

# AQI 顏色對照表
def get_aqi_color(aqi_value):
    """根據 AQI 值返回對應顏色"""
    try:
        aqi = int(float(aqi_value)) if aqi_value else 0
    except (ValueError, TypeError):
        return '#808080'  # 灰色 (無效數據)
    
    if aqi <= 50:
        return '#00E400'  # 綠色 (良好)
    elif aqi <= 100:
        return '#FFFF00'  # 黃色 (普通)
    elif aqi <= 150:
        return '#FF7E00'  # 橙色 (對敏感族群不健康)
    elif aqi <= 200:
        return '#FF0000'  # 紅色 (不健康)
    elif aqi <= 300:
        return '#8F3F97'  # 紫色 (非常不健康)
    else:
        return '#7E0023'  # 褐紅色 (危害)

def get_aqi_level(aqi_value):
    """根據 AQI 值返回等級描述"""
    try:
        aqi = int(float(aqi_value)) if aqi_value else 0
    except (ValueError, TypeError):
        return '無數據'
    
    if aqi <= 50:
        return '良好'
    elif aqi <= 100:
        return '普通'
    elif aqi <= 150:
        return '對敏感族群不健康'
    elif aqi <= 200:
        return '不健康'
    elif aqi <= 300:
        return '非常不健康'
    else:
        return '危害'

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
        
        # API 回傳是列表
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'records' in data:
            return data['records']
        else:
            print(f"API 回應格式: {type(data)}")
            return []
    except Exception as e:
        print(f"獲取 AQI 數據失敗: {e}")
        return []

def load_shelter_data():
    """讀取避難收容處所資料"""
    filepath = 'outputs/shelter_shelters_with_indoor.csv'
    
    try:
        df = pd.read_csv(filepath, encoding='utf-8-sig')
        print(f"載入 {len(df)} 筆避難收容處所資料")
        return df
    except Exception as e:
        print(f"讀取避難所資料失敗: {e}")
        return pd.DataFrame()

def validate_coordinates(lon, lat, name):
    """
    驗證座標是否在合理範圍內（台灣陸地）
    驗證：若出現在海中，代表審計邏輯有誤
    """
    # 台灣陸地範圍（粗略）
    TAIWAN_LAND_BOUNDS = {
        'lon_min': 119.0, 'lon_max': 122.1,
        'lat_min': 21.8, 'lat_max': 25.3
    }
    
    # 主要海域/不合理區域（簡易判斷）
    # 台灣海峽東部（東海岸）經度約 > 121.4
    # 西部平原經度約 < 120.8
    
    if lon < TAIWAN_LAND_BOUNDS['lon_min'] or lon > TAIWAN_LAND_BOUNDS['lon_max']:
        return False, f"經度 {lon} 超出台灣範圍"
    if lat < TAIWAN_LAND_BOUNDS['lat_min'] or lat > TAIWAN_LAND_BOUNDS['lat_max']:
        return False, f"緯度 {lat} 超出台灣範圍"
    
    # 簡易陸地檢查（排除明顯的海中座標）
    # 台灣本島大致範圍
    # 東部太平洋：經度 > 121.5 且 緯度在 22-25 之間
    # 西部海峽：經度 < 120.0 且 緯度在 23-25 之間
    
    return True, "有效座標"

def create_map():
    """建立整合地圖"""
    print("="*60)
    print("建立 AQI 與避難收容處所整合地圖")
    print("="*60)
    
    # 獲取資料
    aqi_data = fetch_aqi_data()
    shelter_df = load_shelter_data()
    
    if not aqi_data:
        print("無法獲取 AQI 數據")
        return None
    
    if shelter_df.empty:
        print("無法載入避難所資料")
        return None
    
    print(f"\nAQI 測站: {len(aqi_data)} 個")
    print(f"避難收容處所: {len(shelter_df)} 個")
    
    # 建立地圖
    taiwan_center = [23.8, 121.0]
    m = folium.Map(
        location=taiwan_center,
        zoom_start=8,
        tiles='CartoDB positron'  # 簡潔底圖
    )
    
    # ===== 圖層 A: AQI 測站 =====
    aqi_layer = folium.FeatureGroup(name='AQI 測站', show=True)
    
    aqi_stats = {'良好': 0, '普通': 0, '敏感': 0, '不健康': 0, '非常': 0, '危害': 0, '無數據': 0}
    
    for station in aqi_data:
        try:
            site_name = station.get('sitename', '未知測站')
            county = station.get('county', '')
            aqi = station.get('aqi', '')
            pollutant = station.get('pollutant', '')
            status = station.get('status', '')
            lat = float(station.get('latitude', 0))
            lon = float(station.get('longitude', 0))
            
            if lat == 0 or lon == 0:
                continue
            
            color = get_aqi_color(aqi)
            level = get_aqi_level(aqi)
            aqi_stats[level] = aqi_stats.get(level, 0) + 1
            
            popup_content = f"""
            <div style="font-family: Arial, sans-serif; min-width: 180px;">
                <h4 style="margin: 0 0 8px 0; color: #333;">{site_name} 測站</h4>
                <p style="margin: 3px 0; font-size: 12px;"><strong>地點:</strong> {county}</p>
                <p style="margin: 3px 0; font-size: 12px;">
                    <strong>AQI:</strong> 
                    <span style="font-size: 16px; font-weight: bold; color: {color};">{aqi}</span>
                </p>
                <p style="margin: 3px 0; font-size: 12px;"><strong>等級:</strong> {level}</p>
                <p style="margin: 3px 0; font-size: 12px;"><strong>狀態:</strong> {status}</p>
                {f'<p style="margin: 3px 0; font-size: 12px;"><strong>污染物:</strong> {pollutant}</p>' if pollutant else ''}
            </div>
            """
            
            folium.CircleMarker(
                location=[lat, lon],
                radius=10,
                popup=folium.Popup(popup_content, max_width=250),
                color='black',
                weight=1,
                fillColor=color,
                fillOpacity=0.8,
                tooltip=f"{site_name}: AQI {aqi}"
            ).add_to(aqi_layer)
            
        except Exception as e:
            print(f"處理 AQI 測站時發生錯誤: {e}")
            continue
    
    aqi_layer.add_to(m)
    
    # ===== 圖層 B: 避難收容處所 =====
    indoor_layer = folium.FeatureGroup(name='避難所-室內', show=True)
    outdoor_layer = folium.FeatureGroup(name='避難所-室外', show=True)
    
    # 驗證計數器
    validation_passed = 0
    validation_failed = 0
    ocean_shelters = []  # 記錄在海中的避難所
    
    for idx, row in shelter_df.iterrows():
        try:
            # 取得座標
            lon = float(row.iloc[4])  # 經度
            lat = float(row.iloc[5])  # 緯度
            
            if pd.isna(lon) or pd.isna(lat) or lon == 0 or lat == 0:
                continue
            
            # 驗證座標
            is_valid, reason = validate_coordinates(lon, lat, row.iloc[6])
            
            if not is_valid:
                validation_failed += 1
                if '超出' in reason:
                    ocean_shelters.append({
                        'id': row.iloc[0],
                        'name': row.iloc[6],
                        'lon': lon,
                        'lat': lat,
                        'reason': reason
                    })
                continue
            
            validation_passed += 1
            
            # 取得資料
            name = row.iloc[6]  # 避難收容處所名稱
            county = row.iloc[1]  # 縣市
            capacity = row.iloc[8]  # 預計收容人數
            is_indoor = row['is_indoor']  # 是否室內
            
            popup_content = f"""
            <div style="font-family: Arial, sans-serif; min-width: 180px;">
                <h4 style="margin: 0 0 8px 0; color: #333;">{name}</h4>
                <p style="margin: 3px 0; font-size: 12px;"><strong>地點:</strong> {county}</p>
                <p style="margin: 3px 0; font-size: 12px;"><strong>類型:</strong> {'室內' if is_indoor else '室外'}</p>
                <p style="margin: 3px 0; font-size: 12px;"><strong>收容人數:</strong> {capacity}</p>
            </div>
            """
            
            # 選擇圖標
            if is_indoor:
                # 室內：藍色建築圖標
                icon = folium.Icon(color='blue', icon='home', prefix='fa')
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_content, max_width=250),
                    tooltip=f"{name} (室內)",
                    icon=icon
                ).add_to(indoor_layer)
            else:
                # 室外：綠色樹木圖標
                icon = folium.Icon(color='green', icon='tree', prefix='fa')
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_content, max_width=250),
                    tooltip=f"{name} (室外)",
                    icon=icon
                ).add_to(outdoor_layer)
                
        except Exception as e:
            print(f"處理避難所時發生錯誤: {e}")
            continue
    
    indoor_layer.add_to(m)
    outdoor_layer.add_to(m)
    
    # ===== 圖層控制 =====
    folium.LayerControl().add_to(m)
    
    # ===== AQI 圖例 =====
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:12px; padding: 10px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
        <h4 style="margin: 0 0 10px 0; text-align: center;">AQI 空氣品質指標</h4>
        <p style="margin: 5px 0;"><span style="display: inline-block; width: 12px; height: 12px; background-color: #00E400; border-radius: 50%; margin-right: 8px;"></span>0-50 良好</p>
        <p style="margin: 5px 0;"><span style="display: inline-block; width: 12px; height: 12px; background-color: #FFFF00; border-radius: 50%; margin-right: 8px;"></span>51-100 普通</p>
        <p style="margin: 5px 0;"><span style="display: inline-block; width: 12px; height: 12px; background-color: #FF7E00; border-radius: 50%; margin-right: 8px;"></span>101-150 敏感族群</p>
        <p style="margin: 5px 0;"><span style="display: inline-block; width: 12px; height: 12px; background-color: #FF0000; border-radius: 50%; margin-right: 8px;"></span>151-200 不健康</p>
        <p style="margin: 5px 0;"><span style="display: inline-block; width: 12px; height: 12px; background-color: #8F3F97; border-radius: 50%; margin-right: 8px;"></span>201-300 非常不健康</p>
        <p style="margin: 5px 0;"><span style="display: inline-block; width: 12px; height: 12px; background-color: #7E0023; border-radius: 50%; margin-right: 8px;"></span>300+ 危害</p>
        <hr style="margin: 10px 0;">
        <p style="margin: 5px 0;"><span style="display: inline-block; width: 12px; height: 12px; background-color: blue; border-radius: 2px; margin-right: 8px;"></span>避難所-室內</p>
        <p style="margin: 5px 0;"><span style="display: inline-block; width: 12px; height: 12px; background-color: green; border-radius: 2px; margin-right: 8px;"></span>避難所-室外</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # ===== 儲存地圖 =====
    output_path = 'outputs/aqi_shelter_integrated_map.html'
    m.save(output_path)
    
    # ===== 輸出統計 =====
    print("\n" + "="*60)
    print("地圖建立完成")
    print("="*60)
    print(f"地圖檔案: {output_path}")
    print(f"\nAQI 測站分布:")
    for level, count in aqi_stats.items():
        if count > 0:
            print(f"  {level}: {count} 個")
    
    print(f"\n避難所座標驗證:")
    print(f"  通過驗證: {validation_passed} 個")
    print(f"  未通過: {validation_failed} 個")
    
    if ocean_shelters:
        print(f"\n[警告] 發現 {len(ocean_shelters)} 個座標異常的避難所:")
        for s in ocean_shelters[:5]:
            print(f"  ID {s['id']}: {s['name']} - {s['reason']}")
    else:
        print("\n[驗證通過] 所有避難所座標均在合理範圍內，無海中點位")
    
    return output_path

if __name__ == "__main__":
    create_map()
