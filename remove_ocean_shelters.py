#!/usr/bin/env python3
"""
移除海上異常避難所
根據用戶提供的清單移除跑到海上的避難所
"""

import pandas as pd
import os

def remove_ocean_shelters():
    """移除跑到海上的避難所"""
    print("="*60)
    print("移除海上異常避難所資料")
    print("="*60)
    
    # 用戶提供的海上異常避難所清單
    ocean_shelters = [
        "臺中市東區樂業國小",      # 地點: 臺中市東區 -> 跑到海上
        "峰谷國小南棟教室",       # 地點: 臺中市霧峰區 -> 跑到海上  
        "追分國小多功能教室"      # 地點: 臺中市大肚區 -> 跑到海上
    ]
    
    # 讀取清理後資料
    input_file = 'outputs/shelter_shelters_cleaned.csv'
    try:
        df = pd.read_csv(input_file, encoding='utf-8-sig')
        print(f"清理後資料: {len(df)} 筆避難所")
    except Exception as e:
        print(f"讀取檔案失敗: {e}")
        return
    
    # 建立移除記錄
    removed_records = []
    remaining_df = df.copy()
    
    # 逐一檢查並移除海上異常避難所
    for shelter_name in ocean_shelters:
        # 查找匹配的記錄（使用部分匹配）
        matches = df[df.iloc[:, 6].str.contains(shelter_name, na=False, case=False)]
        
        if len(matches) > 0:
            print(f"\n移除: {shelter_name}")
            for idx, row in matches.iterrows():
                print(f"  ID: {row.iloc[0]}, 地點: {row.iloc[1]}, 名稱: {row.iloc[6]}")
                print(f"  座標: ({row.iloc[5]}, {row.iloc[4]})")
                
                # 記錄移除的資訊
                removed_records.append({
                    'shelter_id': row.iloc[0],
                    'shelter_name': row.iloc[6],
                    'recorded_county': row.iloc[1],
                    'lat': row.iloc[5],
                    'lon': row.iloc[4],
                    'is_indoor': row['is_indoor'],
                    'capacity': row.iloc[8],
                    'removal_reason': '跑到海上（座標異常）'
                })
                
                # 從剩餘資料中移除
                remaining_df = remaining_df[remaining_df.iloc[:, 0] != row.iloc[0]]
        else:
            print(f"未找到: {shelter_name}")
    
    # 保存最終清理資料
    final_cleaned_file = 'outputs/shelter_shelters_final_cleaned.csv'
    remaining_df.to_csv(final_cleaned_file, index=False, encoding='utf-8-sig')
    
    # 保存移除記錄
    if removed_records:
        removed_df = pd.DataFrame(removed_records)
        ocean_removed_file = 'outputs/shelter_ocean_removed_records.csv'
        removed_df.to_csv(ocean_removed_file, index=False, encoding='utf-8-sig')
        print(f"\n海上異常移除記錄已儲存至: {ocean_removed_file}")
    
    # 輸出統計
    print(f"\n海上異常清理完成:")
    print(f"清理後資料: {len(df)} 筆")
    print(f"移除資料: {len(removed_records)} 筆")
    print(f"最終資料: {len(remaining_df)} 筆")
    print(f"最終清理後資料已儲存至: {final_cleaned_file}")
    
    # 顯示移除的避難所清單
    if removed_records:
        print(f"\n已移除的海上異常避難所:")
        for record in removed_records:
            print(f"  - {record['shelter_name']} ({record['recorded_county']}) - ID: {record['shelter_id']}")
            print(f"    座標: ({record['lat']}, {record['lon']})")
    
    return remaining_df, removed_records

if __name__ == "__main__":
    remove_ocean_shelters()
