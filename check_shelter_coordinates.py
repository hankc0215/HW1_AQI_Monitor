#!/usr/bin/env python3
"""
避難收容處所座標品質檢查
功能：
1. 檢查座標系統（TWD97 vs WGS84）
2. 偵測離群值（台灣邊界外、0,0）
"""

import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# 載入環境變數
load_dotenv(encoding='utf-8')

# 台灣邊界範圍 (WGS84)
TAIWAN_BOUNDS_WGS84 = {
    'lat_min': 21.8,
    'lat_max': 25.3,
    'lon_min': 119.0,
    'lon_max': 122.1
}

# 台灣範圍 (TWD97 - 二度分帶) 約略值
TAIWAN_BOUNDS_TWD97 = {
    'x_min': 150000,  # 約 121.0°E
    'x_max': 350000,  # 約 122.0°E
    'y_min': 2400000, # 約 21.9°N
    'y_max': 2800000  # 約 25.3°N
}

def load_shelter_data(filepath='data/shelter_shelters.csv'):
    """讀取避難收容處所資料"""
    encodings = ['utf-8-sig', 'utf-8', 'big5', 'cp950']
    for enc in encodings:
        try:
            df = pd.read_csv(filepath, encoding=enc)
            print(f"成功讀取: {enc} 編碼")
            return df
        except Exception as e:
            continue
    raise ValueError("無法讀取檔案")

def detect_crs_system(df):
    """
    根據數值範圍判斷座標系統
    - WGS84: 經度 119-122, 緯度 21-26 (度)
    - TWD97: X 150000-350000, Y 2400000-2800000 (公尺)
    """
    print("\n" + "="*60)
    print("座標系統檢測 (CRS Detection)")
    print("="*60)
    
    # 找出座標欄位
    lat_cols = [c for c in df.columns if any(k in c.lower() for k in ['lat', '緯度', 'y', 'northing'])]
    lon_cols = [c for c in df.columns if any(k in c.lower() for k in ['lon', '經度', 'lng', 'x', 'easting'])]
    
    print(f"\n可能的緯度欄位: {lat_cols}")
    print(f"可能的經度欄位: {lon_cols}")
    
    if not lat_cols or not lon_cols:
        print("無法找到座標欄位，請檢查欄位名稱")
        return None, None, None
    
    lat_col = lat_cols[0]
    lon_col = lon_cols[0]
    
    # 分析數值範圍
    lats = pd.to_numeric(df[lat_col], errors='coerce')
    lons = pd.to_numeric(df[lon_col], errors='coerce')
    
    lat_stats = {
        'min': lats.min(),
        'max': lats.max(),
        'mean': lats.mean(),
        'median': lats.median()
    }
    lon_stats = {
        'min': lons.min(),
        'max': lons.max(),
        'mean': lons.mean(),
        'median': lons.median()
    }
    
    print(f"\n--- {lat_col} (緯度/Y) 統計 ---")
    for k, v in lat_stats.items():
        print(f"  {k}: {v:.6f}")
    
    print(f"\n--- {lon_col} (經度/X) 統計 ---")
    for k, v in lon_stats.items():
        print(f"  {k}: {v:.6f}")
    
    # 判斷座標系統
    lat_range = lat_stats['max'] - lat_stats['min']
    lon_range = lon_stats['max'] - lon_stats['min']
    
    detected_crs = None
    
    # WGS84 特徵：數值範圍小（度數），經度約 119-122，緯度約 21-25
    if (20 < lat_stats['min'] < 30 and 100 < lon_stats['min'] < 130):
        detected_crs = "EPSG:4326 (WGS84)"
        print("\n[結論] 檢測到 WGS84 (經緯度) 座標系統")
    # TWD97 特徵：數值大（公尺），X 約 15-30 萬，Y 約 240-280 萬
    elif (lat_stats['min'] > 1000000 or lon_stats['min'] > 100000):
        detected_crs = "EPSG:3826 (TWD97 / TM2)"
        print("\n[結論] 檢測到 TWD97 二度分帶座標系統")
    else:
        detected_crs = "UNKNOWN"
        print("\n[警告] 無法確定座標系統，數值範圍異常")
    
    return detected_crs, lat_col, lon_col

def detect_outliers(df, lat_col, lon_col, crs_type):
    """偵測離群值"""
    print("\n" + "="*60)
    print("離群值檢測 (Outlier Detection)")
    print("="*60)
    
    lats = pd.to_numeric(df[lat_col], errors='coerce')
    lons = pd.to_numeric(df[lon_col], errors='coerce')
    
    outliers = {
        'zero_coords': [],  # (0,0)
        'null_coords': [],  # 空值
        'out_of_bounds': [],  # 超出台灣範圍
        'duplicate_coords': []  # 重複座標
    }
    
    # 檢查 (0,0)
    zero_mask = (lats == 0) & (lons == 0)
    outliers['zero_coords'] = df[zero_mask].index.tolist()
    
    # 檢查空值
    null_mask = lats.isnull() | lons.isnull()
    outliers['null_coords'] = df[null_mask].index.tolist()
    
    # 檢查台灣範圍
    if "WGS84" in crs_type:
        bounds = TAIWAN_BOUNDS_WGS84
        out_of_bounds_mask = (
            (lats < bounds['lat_min']) | (lats > bounds['lat_max']) |
            (lons < bounds['lon_min']) | (lons > bounds['lon_max'])
        )
    else:
        bounds = TAIWAN_BOUNDS_TWD97
        out_of_bounds_mask = (
            (lats < bounds['y_min']) | (lats > bounds['y_max']) |
            (lons < bounds['x_min']) | (lons > bounds['x_max'])
        )
    
    outliers['out_of_bounds'] = df[out_of_bounds_mask].index.tolist()
    
    # 檢查重複座標
    coords_df = pd.DataFrame({'lat': lats, 'lon': lons}).dropna()
    dupes = coords_df[coords_df.duplicated(keep=False)]
    outliers['duplicate_coords'] = dupes.index.tolist()
    
    # 輸出結果
    print(f"\n--- 異常統計 ---")
    print(f"  (0,0) 座標: {len(outliers['zero_coords'])} 筆")
    print(f"  空值座標: {len(outliers['null_coords'])} 筆")
    print(f"  台灣範圍外: {len(outliers['out_of_bounds'])} 筆")
    print(f"  重複座標: {len(outliers['duplicate_coords'])} 筆")
    
    # 顯示前幾個異常範例
    if outliers['zero_coords']:
        print("\n  (0,0) 座標範例:")
        for idx in outliers['zero_coords'][:3]:
            row = df.iloc[idx]
            print(f"    ID {row.iloc[0]}: {row.get('避難收容處所名稱', 'N/A')}")
    
    if outliers['out_of_bounds']:
        print("\n  範圍外座標範例:")
        for idx in outliers['out_of_bounds'][:3]:
            row = df.iloc[idx]
            lat_val = lats.iloc[idx]
            lon_val = lons.iloc[idx]
            print(f"    ID {row.iloc[0]}: ({lon_val:.4f}, {lat_val:.4f}) - {row.get('避難收容處所名稱', 'N/A')}")
    
    return outliers

def export_clean_data(df, outliers, lat_col, lon_col):
    """匯出清理後的資料"""
    print("\n" + "="*60)
    print("資料清理結果")
    print("="*60)
    
    # 建立有效資料遮罩
    valid_mask = pd.Series([True] * len(df), index=df.index)
    
    for outlier_type, indices in outliers.items():
        if indices:
            valid_mask.loc[indices] = False
    
    valid_count = valid_mask.sum()
    invalid_count = (~valid_mask).sum()
    
    print(f"\n  總筆數: {len(df)}")
    print(f"  有效座標: {valid_count} ({valid_count/len(df)*100:.1f}%)")
    print(f"  異常座標: {invalid_count} ({invalid_count/len(df)*100:.1f}%)")
    
    # 儲存有效資料
    valid_df = df[valid_mask].copy()
    output_path = 'outputs/shelter_shelters_valid.csv'
    os.makedirs('outputs', exist_ok=True)
    valid_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n  有效資料已儲存至: {output_path}")
    
    # 儲存異常資料
    invalid_df = df[~valid_mask].copy()
    invalid_path = 'outputs/shelter_shelters_invalid.csv'
    invalid_df.to_csv(invalid_path, index=False, encoding='utf-8-sig')
    print(f"  異常資料已儲存至: {invalid_path}")
    
    return valid_df

def main():
    print("避難收容處所座標品質檢查工具")
    print("="*60)
    
    # 載入資料
    df = load_shelter_data()
    print(f"\n載入 {len(df)} 筆避難收容處所資料")
    print(f"欄位: {list(df.columns)}")
    
    # 檢測座標系統
    crs_type, lat_col, lon_col = detect_crs_system(df)
    
    if crs_type and lat_col and lon_col:
        # 偵測離群值
        outliers = detect_outliers(df, lat_col, lon_col, crs_type)
        
        # 匯出清理資料
        valid_df = export_clean_data(df, outliers, lat_col, lon_col)
        
        # 摘要報告
        print("\n" + "="*60)
        print("分析摘要")
        print("="*60)
        print(f"座標系統: {crs_type}")
        print(f"緯度/Y 欄位: {lat_col}")
        print(f"經度/X 欄位: {lon_col}")
        print(f"有效資料: {len(valid_df)}/{len(df)} 筆")
    else:
        print("無法繼續分析，請檢查資料格式")

if __name__ == "__main__":
    main()
