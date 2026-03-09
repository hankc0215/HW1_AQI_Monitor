#!/usr/bin/env python3
"""
重新進行最終清理後資料的位置驗證
使用最終清理後的避難所資料重新驗證位置準確性
"""

import pandas as pd
import requests
import json
import time
from typing import Dict, List, Tuple
import os

# 台灣各縣市的大致邊界（放寬版）
TAIWAN_COUNTY_BOUNDS = {
    '新北市': [121.1, 122.3, 24.6, 25.5],
    '臺北市': [121.2, 121.9, 24.7, 25.4],
    '基隆市': [121.4, 122.0, 25.0, 25.5],
    '桃園市': [120.8, 121.6, 24.4, 25.3],
    '新竹縣': [120.6, 121.5, 24.1, 25.0],
    '新竹市': [120.7, 121.3, 24.4, 25.1],
    '苗栗縣': [120.4, 121.4, 23.9, 24.9],
    '臺中市': [120.3, 121.5, 23.8, 24.6],
    '彰化縣': [120.1, 120.9, 23.6, 24.4],
    '南投縣': [120.4, 121.5, 23.4, 24.4],
    '雲林縣': [120.0, 120.8, 23.3, 24.1],
    '嘉義縣': [120.0, 120.9, 23.1, 23.8],
    '嘉義市': [120.2, 120.8, 23.2, 23.8],
    '臺南市': [119.9, 120.7, 22.6, 23.6],
    '高雄市': [120.0, 120.9, 22.2, 23.4],
    '屏東縣': [120.3, 121.2, 21.7, 23.0],
    '宜蘭縣': [121.4, 122.2, 24.1, 25.0],
    '花蓮縣': [121.0, 121.9, 22.7, 24.4],
    '臺東縣': [120.6, 121.6, 22.1, 23.4],
    '澎湖縣': [119.2, 119.9, 23.2, 23.9],
    '金門縣': [118.0, 118.7, 24.1, 24.7],
    '連江縣': [119.7, 120.4, 25.9, 26.6]
}

def is_point_in_county(lat: float, lon: float, county: str) -> bool:
    """檢查點是否位於指定縣市邊界內"""
    if county not in TAIWAN_COUNTY_BOUNDS:
        return False
    
    min_lon, max_lon, min_lat, max_lat = TAIWAN_COUNTY_BOUNDS[county]
    
    return (min_lon <= lon <= max_lon) and (min_lat <= lat <= max_lat)

def is_point_far_from_county(lat: float, lon: float, county: str) -> bool:
    """檢查點是否遠離縣市邊界（超出太多）"""
    # 原始嚴格邊界
    STRICT_BOUNDS = {
        '新北市': [121.3, 122.1, 24.8, 25.3],
        '臺北市': [121.4, 121.7, 24.9, 25.2],
        '基隆市': [121.6, 121.8, 25.1, 25.3],
        '桃園市': [121.0, 121.4, 24.6, 25.1],
        '新竹縣': [120.8, 121.3, 24.3, 24.8],
        '新竹市': [120.9, 121.1, 24.6, 24.9],
        '苗栗縣': [120.6, 121.2, 24.1, 24.7],
        '臺中市': [120.5, 121.3, 24.0, 24.4],
        '彰化縣': [120.3, 120.7, 23.8, 24.2],
        '南投縣': [120.6, 121.3, 23.6, 24.2],
        '雲林縣': [120.2, 120.6, 23.5, 23.9],
        '嘉義縣': [120.2, 120.7, 23.3, 23.6],
        '嘉義市': [120.4, 120.6, 23.4, 23.6],
        '臺南市': [120.1, 120.5, 22.8, 23.4],
        '高雄市': [120.2, 120.7, 22.4, 23.2],
        '屏東縣': [120.5, 121.0, 21.9, 22.8],
        '宜蘭縣': [121.6, 122.0, 24.3, 24.8],
        '花蓮縣': [121.2, 121.7, 22.9, 24.2],
        '臺東縣': [120.8, 121.4, 22.3, 23.2],
        '澎湖縣': [119.4, 119.7, 23.4, 23.7],
        '金門縣': [118.2, 118.5, 24.3, 24.5],
        '連江縣': [119.9, 120.2, 26.1, 26.4]
    }
    
    if county not in STRICT_BOUNDS:
        return True  # 未知縣市標記為遠離
    
    min_lon, max_lon, min_lat, max_lat = STRICT_BOUNDS[county]
    
    # 計算超出邊界的距離
    lon_offset = 0
    lat_offset = 0
    
    if lon < min_lon:
        lon_offset = min_lon - lon
    elif lon > max_lon:
        lon_offset = lon - max_lon
    
    if lat < min_lat:
        lat_offset = min_lat - lat
    elif lat > max_lat:
        lat_offset = lat - max_lat
    
    # 如果超出邊界超過 0.1 度（約 11km），標記為遠離
    return lon_offset > 0.1 or lat_offset > 0.1

def get_reverse_geocode(lat: float, lon: float) -> Dict:
    """使用逆地理編碼獲取座標對應的地址資訊"""
    try:
        time.sleep(1)
        
        url = f"https://nominatim.openstreetmap.org/reverse"
        params = {
            'format': 'json',
            'lat': lat,
            'lon': lon,
            'accept-language': 'zh-TW,zh'
        }
        
        headers = {
            'User-Agent': 'AQI Shelter Location Validator (Final Cleaned)'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'address': data.get('address', {}),
                'display_name': data.get('display_name', ''),
                'county': extract_county_from_address(data.get('address', {})),
                'township': extract_township_from_address(data.get('address', {}))
            }
        else:
            return {'success': False, 'error': f'HTTP {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def extract_county_from_address(address: Dict) -> str:
    """從地址資訊中提取縣市"""
    for key in ['state', 'county', 'city']:
        if key in address and address[key]:
            value = address[key]
            if '市' in value or '縣' in value:
                return value
    return ''

def extract_township_from_address(address: Dict) -> str:
    """從地址資訊中提取鄉鎮市區"""
    for key in ['suburb', 'town', 'village', 'district']:
        if key in address and address[key]:
            return address[key]
    return ''

def load_final_cleaned_shelter_data():
    """讀取最終清理後的避難所資料"""
    filepath = 'outputs/shelter_shelters_final_cleaned.csv'
    
    try:
        df = pd.read_csv(filepath, encoding='utf-8-sig')
        print(f"載入 {len(df)} 筆最終清理後的避難收容處所資料")
        return df
    except Exception as e:
        print(f"讀取最終清理後避難所資料失敗: {e}")
        return pd.DataFrame()

def validate_final_cleaned_shelter_locations():
    """驗證最終清理後避難所位置"""
    print("="*70)
    print("最終清理後避難所位置驗證")
    print("="*70)
    
    # 載入資料
    shelter_df = load_final_cleaned_shelter_data()
    
    if shelter_df.empty:
        print("無法載入最終清理後避難所資料")
        return None
    
    print(f"開始驗證 {len(shelter_df)} 個最終清理後避難所位置...")
    
    # 統計計數器
    county_mismatch = 0
    township_mismatch = 0
    geocode_failed = 0
    validation_results = []
    
    for idx, row in shelter_df.iterrows():
        try:
            # 取得避難所資料
            shelter_id = row.iloc[0]
            shelter_name = row.iloc[6]
            recorded_county = row.iloc[1]  # 記錄的縣市
            shelter_lat = float(row.iloc[5])
            shelter_lon = float(row.iloc[4])
            
            if shelter_lat == 0 or shelter_lon == 0:
                continue
            
            # 1. 檢查是否在台灣範圍內
            taiwan_bounds = [119.0, 122.1, 21.8, 25.3]
            if not (taiwan_bounds[0] <= shelter_lon <= taiwan_bounds[1] and 
                   taiwan_bounds[2] <= shelter_lat <= taiwan_bounds[3]):
                continue
            
            # 2. 基本邊界檢查（放寬版）
            county_in_bounds = is_point_in_county(shelter_lat, shelter_lon, recorded_county)
            
            # 3. 遠離邊界檢查（嚴格版）
            is_far_from_county = is_point_far_from_county(shelter_lat, shelter_lon, recorded_county)
            
            # 4. 逆地理編碼驗證（抽樣檢查）
            geocode_result = {'success': False}
            
            # 只對前50個進行詳細驗證（避免API限制）
            if idx < 50:
                geocode_result = get_reverse_geocode(shelter_lat, shelter_lon)
                
                if not geocode_result['success']:
                    geocode_failed += 1
                    print(f"  逆地理編碼失敗: {shelter_name} - {geocode_result.get('error', 'Unknown error')}")
            
            # 5. 分析結果
            result = {
                'shelter_id': shelter_id,
                'shelter_name': shelter_name,
                'recorded_county': recorded_county,
                'lat': shelter_lat,
                'lon': shelter_lon,
                'county_in_bounds': county_in_bounds,
                'far_from_county': is_far_from_county,
                'geocode_success': geocode_result['success'],
                'geocoded_county': geocode_result.get('county', '') if geocode_result['success'] else '',
                'geocoded_township': geocode_result.get('township', '') if geocode_result['success'] else '',
                'display_name': geocode_result.get('display_name', '') if geocode_result['success'] else '',
                'county_match': False,
                'township_match': False,
                'issues': [],
                'data_source': 'final_cleaned'  # 標記為最終清理後資料
            }
            
            # 檢查縣市匹配
            if geocode_result['success'] and geocode_result.get('county'):
                geocoded_county = geocode_result.get('county', '')
                
                county_match = False
                if recorded_county in geocoded_county or geocoded_county in recorded_county:
                    county_match = True
                elif '市' in recorded_county and '市' in geocoded_county:
                    if recorded_county.replace('市', '') in geocoded_county.replace('市', ''):
                        county_match = True
                elif '縣' in recorded_county and '縣' in geocoded_county:
                    if recorded_county.replace('縣', '') in geocoded_county.replace('縣', ''):
                        county_match = True
                
                result['county_match'] = county_match
                
                if not county_match:
                    county_mismatch += 1
                    result['issues'].append(f"縣市不匹配: 記錄={recorded_county}, 實際={geocoded_county}")
            
            # 檢查鄉鎮匹配
            if geocode_result['success'] and geocode_result.get('township'):
                shelter_township = ''
                if '鄉' in shelter_name or '鎮' in shelter_name or '區' in shelter_name:
                    for suffix in ['鄉', '鎮', '區']:
                        if suffix in shelter_name:
                            parts = shelter_name.split(suffix)
                            if len(parts) > 1:
                                shelter_township = parts[0] + suffix
                                break
                
                geocoded_township = geocode_result.get('township', '')
                
                township_match = False
                if shelter_township and geocoded_township:
                    if shelter_township in geocoded_township or geocoded_township in shelter_township:
                        township_match = True
                
                result['township_match'] = township_match
                result['shelter_township'] = shelter_township
                
                if not township_match and shelter_township:
                    township_mismatch += 1
                    result['issues'].append(f"鄉鎮不匹配: 名稱={shelter_township}, 實際={geocoded_township}")
            
            # 檢查邊界問題
            if is_far_from_county:
                result['issues'].append("座標遠離記錄縣市邊界（超出11公里以上）")
            elif not county_in_bounds:
                result['issues'].append("座標在記錄縣市邊界邊緣（容許範圍）")
            
            validation_results.append(result)
            
            # 進度顯示
            if (idx + 1) % 50 == 0:
                print(f"已處理 {idx + 1}/{len(shelter_df)} 個最終清理後避難所...")
                
        except Exception as e:
            print(f"處理最終清理後避難所 {idx} 時發生錯誤: {e}")
            continue
    
    # 轉換為 DataFrame
    results_df = pd.DataFrame(validation_results)
    
    # 輸出統計
    print(f"\n最終清理後驗證完成!")
    print(f"總共驗證: {len(results_df)} 個最終清理後避難所")
    print(f"縣市不匹配: {county_mismatch} 個")
    print(f"鄉鎮不匹配: {township_mismatch} 個")
    print(f"逆地理編碼失敗: {geocode_failed} 個")
    
    # 統計邊界問題
    far_boundary = results_df[results_df['far_from_county'] == True]
    edge_boundary = results_df[(results_df['far_from_county'] == False) & 
                            (results_df['county_in_bounds'] == False)]
    
    print(f"遠離邊界（>11km）: {len(far_boundary)} 個")
    print(f"邊界邊緣（容許範圍）: {len(edge_boundary)} 個")
    
    # 顯示問題案例
    problematic = results_df[results_df['issues'].apply(len) > 0]
    print(f"\n發現位置問題的最終清理後避難所: {len(problematic)} 個")
    
    if len(problematic) > 0:
        print("\n問題案例 (前10筆):")
        for _, row in problematic.head(10).iterrows():
            print(f"  {row['shelter_name']} ({row['recorded_county']})")
            for issue in row['issues']:
                print(f"    - {issue}")
            if row['display_name']:
                print(f"    實際地址: {row['display_name']}")
    
    # 保存結果
    output_path = 'outputs/shelter_location_validation_final.csv'
    results_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n最終清理後驗證結果已儲存至: {output_path}")
    
    # 生成問題清單
    if len(problematic) > 0:
        problem_path = 'outputs/shelter_location_issues_final.csv'
        problematic.to_csv(problem_path, index=False, encoding='utf-8-sig')
        print(f"最終清理後問題清單已儲存至: {problem_path}")
    
    return results_df

if __name__ == "__main__":
    validate_final_cleaned_shelter_locations()
