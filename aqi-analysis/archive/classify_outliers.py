#!/usr/bin/env python3
"""
離島與異常座標分類器
將離群值分為：
- 離島（正常，保留）
- 錯誤座標（需排除）
"""

import pandas as pd
import numpy as np

# 離島縣市列表
OUTLYING_ISLANDS = {
    '金門縣', '連江縣', '澎湖縣', '臺東縣'  # 臺東縣包含蘭嶼、綠島
}

def classify_outliers():
    # 載入資料
    df = pd.read_csv('data/shelter_shelters.csv', encoding='utf-8-sig')
    
    # 取得座標欄位
    lons = pd.to_numeric(df.iloc[:, 4], errors='coerce')
    lats = pd.to_numeric(df.iloc[:, 5], errors='coerce')
    counties = df.iloc[:, 1]  # 縣市鄉鎮區
    
    # 台灣本島邊界
    TAIWAN_LON_MIN, TAIWAN_LON_MAX = 119.0, 122.1
    TAIWAN_LAT_MIN, TAIWAN_LAT_MAX = 21.8, 25.3
    
    # 找出離群值
    out_mask = (
        (lons < TAIWAN_LON_MIN) | (lons > TAIWAN_LON_MAX) |
        (lats < TAIWAN_LAT_MIN) | (lats > TAIWAN_LAT_MAX)
    )
    
    results = {
        'island_data': [],      # 離島（保留）
        'error_data': [],       # 錯誤座標（排除）
        'uncertain_data': []    # 需人工確認
    }
    
    for idx in df[out_mask].index:
        row = df.iloc[idx]
        county_full = row.iloc[1]
        lon = lons.iloc[idx]
        lat = lats.iloc[idx]
        
        # 判斷縣市
        is_island = any(island in county_full for island in OUTLYING_ISLANDS)
        
        # 明顯錯誤
        if lon == 0.0:
            results['error_data'].append({
                'index': idx,
                'id': row.iloc[0],
                'county': county_full,
                'name': row.iloc[6],
                'lon': lon,
                'lat': lat,
                'reason': '經度為 0.0（缺失資料）'
            })
        # 離島
        elif is_island:
            results['island_data'].append({
                'index': idx,
                'id': row.iloc[0],
                'county': county_full,
                'name': row.iloc[6],
                'lon': lon,
                'lat': lat,
                'reason': '離島區域'
            })
        # 桃園市異常（緯度 > 26.9，明顯錯誤）
        elif '桃園市' in county_full and lat > 26.5:
            results['error_data'].append({
                'index': idx,
                'id': row.iloc[0],
                'county': county_full,
                'name': row.iloc[6],
                'lon': lon,
                'lat': lat,
                'reason': f'桃園市緯度異常過高 ({lat:.4f})'
            })
        # 其他異常（本島但超出邊界）
        else:
            reasons = []
            if lon < TAIWAN_LON_MIN:
                reasons.append(f'經度過低 ({lon:.4f} < 119.0)')
            if lon > TAIWAN_LON_MAX:
                reasons.append(f'經度過高 ({lon:.4f} > 122.1)')
            if lat < TAIWAN_LAT_MIN:
                reasons.append(f'緯度過低 ({lat:.4f} < 21.8)')
            if lat > TAIWAN_LAT_MAX:
                reasons.append(f'緯度過高 ({lat:.4f} > 25.3)')
            
            results['uncertain_data'].append({
                'index': idx,
                'id': row.iloc[0],
                'county': county_full,
                'name': row.iloc[6],
                'lon': lon,
                'lat': lat,
                'reason': ' + '.join(reasons)
            })
    
    return results

def print_report(results):
    """輸出分析報告"""
    print("="*70)
    print("離島與異常座標分類報告")
    print("="*70)
    
    # 離島資料
    island_df = pd.DataFrame(results['island_data'])
    print(f"\n【1】離島區域（正常資料，建議保留）: {len(island_df)} 筆")
    print("-"*70)
    if len(island_df) > 0:
        print(island_df.groupby('county').size().to_string())
    
    # 明顯錯誤
    error_df = pd.DataFrame(results['error_data'])
    print(f"\n【2】明顯錯誤座標（建議排除）: {len(error_df)} 筆")
    print("-"*70)
    for _, row in error_df.iterrows():
        print(f"  ID {row['id']}: {row['county']} - {row['name']}")
        print(f"      ({row['lon']:.4f}, {row['lat']:.4f}) - {row['reason']}")
    
    # 需確認
    uncertain_df = pd.DataFrame(results['uncertain_data'])
    print(f"\n【3】需人工確認: {len(uncertain_df)} 筆")
    print("-"*70)
    for _, row in uncertain_df.iterrows():
        print(f"  ID {row['id']}: {row['county']} - {row['name']}")
        print(f"      ({row['lon']:.4f}, {row['lat']:.4f}) - {row['reason']}")
    
    # 建議操作
    print("\n" + "="*70)
    print("建議操作")
    print("="*70)
    print(f"  保留（離島）: {len(island_df)} 筆")
    print(f"  排除（錯誤）: {len(error_df)} 筆")
    print(f"  人工確認: {len(uncertain_df)} 筆")
    print(f"  總計處理: {len(island_df) + len(error_df) + len(uncertain_df)} 筆")
    
    return island_df, error_df, uncertain_df

def export_clean_dataset(results):
    """匯出清理後的資料集"""
    df = pd.read_csv('data/shelter_shelters.csv', encoding='utf-8-sig')
    
    # 建立標記欄位
    df['coordinate_status'] = 'valid'  # 預設有效
    df['exclude_reason'] = ''
    
    # 標記錯誤資料
    for item in results['error_data']:
        df.loc[item['index'], 'coordinate_status'] = 'error'
        df.loc[item['index'], 'exclude_reason'] = item['reason']
    
    # 標記需確認資料
    for item in results['uncertain_data']:
        df.loc[item['index'], 'coordinate_status'] = 'review'
        df.loc[item['index'], 'exclude_reason'] = item['reason']
    
    # 標記離島資料
    for item in results['island_data']:
        df.loc[item['index'], 'coordinate_status'] = 'island'
        df.loc[item['index'], 'exclude_reason'] = 'outlying_island'
    
    # 儲存完整標記檔案
    import os
    os.makedirs('outputs', exist_ok=True)
    df.to_csv('outputs/shelter_shelters_classified.csv', index=False, encoding='utf-8-sig')
    print("\n完整標記檔案已儲存: outputs/shelter_shelters_classified.csv")
    
    # 儲存有效資料（本島 + 離島）
    valid_df = df[df['coordinate_status'].isin(['valid', 'island'])].copy()
    valid_df.to_csv('outputs/shelter_shelters_main_valid.csv', index=False, encoding='utf-8-sig')
    print(f"有效資料（本島+離島）已儲存: outputs/shelter_shelters_main_valid.csv ({len(valid_df)} 筆)")
    
    # 儲存純本島資料（排除離島和錯誤）
    main_island_df = df[df['coordinate_status'] == 'valid'].copy()
    main_island_df.to_csv('outputs/shelter_shelters_main_island_only.csv', index=False, encoding='utf-8-sig')
    print(f"純本島資料已儲存: outputs/shelter_shelters_main_island_only.csv ({len(main_island_df)} 筆)")
    
    # 儲存需排除資料
    exclude_df = df[df['coordinate_status'].isin(['error', 'review'])].copy()
    exclude_df.to_csv('outputs/shelter_shelters_to_review.csv', index=False, encoding='utf-8-sig')
    print(f"需排除/確認資料已儲存: outputs/shelter_shelters_to_review.csv ({len(exclude_df)} 筆)")

def main():
    results = classify_outliers()
    island_df, error_df, uncertain_df = print_report(results)
    export_clean_dataset(results)
    
    print("\n" + "="*70)
    print("後續分析建議")
    print("="*70)
    print("  選項 A: 分析台灣本島 + 離島 → 使用 shelter_shelters_main_valid.csv")
    print("  選項 B: 僅分析台灣本島 → 使用 shelter_shelters_main_island_only.csv")
    print("  選項 C: 全部資料 → 使用原始檔案，但注意 25 筆錯誤座標")

if __name__ == "__main__":
    main()
