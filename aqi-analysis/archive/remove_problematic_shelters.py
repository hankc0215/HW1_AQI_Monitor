#!/usr/bin/env python3
"""
移除明顯錯誤的避難所資料
根據用戶提供的清單移除位置錯誤的避難所
"""

import pandas as pd
import os

def remove_problematic_shelters():
    """移除明顯錯誤的避難所"""
    print("="*60)
    print("移除明顯錯誤的避難所資料")
    print("="*60)
    
    # 用戶提供的錯誤避難所清單
    problematic_shelters = [
        "忠孝國小",           # 地點: 彰化市 -> 實際可能在其他縣市
        "松林社區活動中心",     # 地點: 新竹縣新豐鄉 -> 位置錯誤
        "霧峰國中行政大樓地下室", # 地點: 臺中市霧峰區 -> 重複項目
        "霧峰國小志文樓地下室", # 地點: 臺中市霧峰區 -> 重複項目
        "霧峰國中行政大樓地下室", # 地點: 臺中市霧峰區 -> 重複項目
        "新豐社區活動中心",     # 地點: 南投縣草屯鎮 -> 應為新竹縣新豐鄉
        "土牛活動中心",        # 地點: 臺中市石岡區 -> 位置錯誤
        "高雄市大樹區姑山國民小學", # 地點: 高雄市大樹區 -> 位置錯誤
        "湖口鄉信勢國小禮堂"   # 地點: 新竹縣湖口鄉 -> 位置錯誤
    ]
    
    # 讀取原始資料
    input_file = 'outputs/shelter_shelters_with_indoor.csv'
    try:
        df = pd.read_csv(input_file, encoding='utf-8-sig')
        print(f"原始資料: {len(df)} 筆避難所")
    except Exception as e:
        print(f"讀取檔案失敗: {e}")
        return
    
    # 建立移除記錄
    removed_records = []
    remaining_df = df.copy()
    
    # 逐一檢查並移除問題避難所
    for shelter_name in problematic_shelters:
        # 查找匹配的記錄（使用部分匹配）
        matches = df[df.iloc[:, 6].str.contains(shelter_name, na=False, case=False)]
        
        if len(matches) > 0:
            print(f"\n移除: {shelter_name}")
            for idx, row in matches.iterrows():
                print(f"  ID: {row.iloc[0]}, 地點: {row.iloc[1]}, 名稱: {row.iloc[6]}")
                
                # 記錄移除的資訊
                removed_records.append({
                    'shelter_id': row.iloc[0],
                    'shelter_name': row.iloc[6],
                    'recorded_county': row.iloc[1],
                    'lat': row.iloc[5],
                    'lon': row.iloc[4],
                    'is_indoor': row['is_indoor'],
                    'capacity': row.iloc[8],
                    'removal_reason': '用戶標記的位置錯誤'
                })
                
                # 從剩餘資料中移除
                remaining_df = remaining_df[remaining_df.iloc[:, 0] != row.iloc[0]]
        else:
            print(f"未找到: {shelter_name}")
    
    # 保存清理後的資料
    cleaned_file = 'outputs/shelter_shelters_cleaned.csv'
    remaining_df.to_csv(cleaned_file, index=False, encoding='utf-8-sig')
    
    # 保存移除記錄
    if removed_records:
        removed_df = pd.DataFrame(removed_records)
        removed_file = 'outputs/shelter_removed_records.csv'
        removed_df.to_csv(removed_file, index=False, encoding='utf-8-sig')
        print(f"\n移除記錄已儲存至: {removed_file}")
    
    # 輸出統計
    print(f"\n清理完成:")
    print(f"原始資料: {len(df)} 筆")
    print(f"移除資料: {len(removed_records)} 筆")
    print(f"剩餘資料: {len(remaining_df)} 筆")
    print(f"清理後資料已儲存至: {cleaned_file}")
    
    # 顯示移除的避難所清單
    if removed_records:
        print(f"\n已移除的避難所:")
        for record in removed_records:
            print(f"  - {record['shelter_name']} ({record['recorded_county']}) - ID: {record['shelter_id']}")
    
    return remaining_df, removed_records

if __name__ == "__main__":
    remove_problematic_shelters()
