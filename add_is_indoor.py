#!/usr/bin/env python3
"""
新增 is_indoor 欄位
根據設施名稱關鍵字判斷是否為室內避難所
"""

import pandas as pd
import re

# 室內設施關鍵字（優先匹配）
INDOOR_KEYWORDS = [
    '國小', '國中', '高中', '小學', '中學',  # 學校
    '教室', '禮堂', '活動中心', '集會所',
    '體育館', '運動中心',
    '活動中心', '社區中心', '里辦公處', '村辦公處',
    '教會', '教堂', '寺廟', '宮', '廟', '祠',
    '福利中心', '文康中心',
    '圖書館', '博物館', '藝文中心',
    '禮堂', '演藝廳',
    '醫院', '衛生所',
    '警察局', '消防局', '分局',
    '辦公處', '公所',
    '宿舍', '公寓',
]

# 室外設施關鍵字（優先匹配）
OUTDOOR_KEYWORDS = [
    '公園', '廣場', '公園',
    '球場', '操場', '田徑場',
    '停車場', '停車棚',
    '道路', '橋梁',
    '空地', '閒置空間',
    '公園', '綠地',
    '滯洪池', '水池',
    '風景區', '管理處',  # <-- 新增：風景區相關
]

def classify_indoor(name):
    """
    根據設施名稱判斷是否為室內
    Returns: True (室內), False (室外)
    無法判斷的預設為室內（True）
    """
    if pd.isna(name) or not isinstance(name, str):
        return True  # 無法判斷 -> 預設室內
    
    name = str(name).strip()
    
    # 優先檢查室外關鍵字
    for keyword in OUTDOOR_KEYWORDS:
        if keyword in name:
            return False
    
    # 檢查室內關鍵字
    for keyword in INDOOR_KEYWORDS:
        if keyword in name:
            return True
    
    # 無法判斷 -> 預設室內
    return True

def add_is_indoor_column():
    """新增 is_indoor 欄位到資料集"""
    # 讀取資料
    df = pd.read_csv('outputs/shelter_shelters_main_valid.csv', encoding='utf-8-sig')
    
    print(f"載入 {len(df)} 筆避難收容處所資料")
    
    # 設施名稱欄位（第7欄，索引6）
    facility_names = df.iloc[:, 6]
    
    # 套用分類
    is_indoor_list = []
    unclassified = []
    
    for idx, name in enumerate(facility_names):
        result = classify_indoor(name)
        is_indoor_list.append(result)
        
        if result is None:
            unclassified.append((idx, name))
    
    # 新增欄位
    df['is_indoor'] = is_indoor_list
    
    # 統計結果
    indoor_count = sum(1 for x in is_indoor_list if x is True)
    outdoor_count = sum(1 for x in is_indoor_list if x is False)
    unknown_count = sum(1 for x in is_indoor_list if x is None)
    
    print("\n" + "="*60)
    print("is_indoor 分類統計")
    print("="*60)
    print(f"  室內 (True): {indoor_count} 筆 ({indoor_count/len(df)*100:.1f}%)")
    print(f"  室外 (False): {outdoor_count} 筆 ({outdoor_count/len(df)*100:.1f}%)")
    print(f"  無法判斷 (None): {unknown_count} 筆 ({unknown_count/len(df)*100:.1f}%)")
    
    # 顯示無法判斷的範例
    if unclassified:
        print("\n無法自動分類的設施範例（前10筆）:")
        for idx, name in unclassified[:10]:
            row_id = df.iloc[idx, 0]
            county = df.iloc[idx, 1]
            print(f"  ID {row_id}: {name} ({county})")
    
    # 儲存結果
    output_path = 'outputs/shelter_shelters_with_indoor.csv'
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n結果已儲存至: {output_path}")
    
    return df

def validate_with_existing_columns(df):
    """驗證與既有室內/室外欄位的一致性"""
    # 既有欄位在索引 12, 13（室內、室外）
    existing_indoor = df.iloc[:, 12]  # 室內欄位
    existing_outdoor = df.iloc.iloc[:, 13]  # 室外欄位
    
    matches = 0
    mismatches = []
    
    for idx in range(len(df)):
        our_result = df.loc[idx, 'is_indoor']
        existing = existing_indoor.iloc[idx]
        
        if our_result is True and existing == '是':
            matches += 1
        elif our_result is False and existing == '否':
            matches += 1
        elif our_result is None:
            continue  # 我們無法判斷，跳過
        else:
            mismatches.append((
                df.iloc[idx, 0],  # ID
                df.iloc[idx, 6],  # 名稱
                our_result,
                existing
            ))
    
    print(f"\n與既有室內/室外欄位一致性: {matches}/{len(df)} ({matches/len(df)*100:.1f}%)")
    
    if mismatches:
        print(f"\n不一致案例（前5筆）:")
        for row in mismatches[:5]:
            print(f"  ID {row[0]}: {row[1]} - 我們判斷={row[2]}, 既有資料={row[3]}")

if __name__ == "__main__":
    df = add_is_indoor_column()
    
    # 顯示分類範例
    print("\n" + "="*60)
    print("分類範例")
    print("="*60)
    
    indoor_examples = df[df['is_indoor'] == True].iloc[:5]
    outdoor_examples = df[df['is_indoor'] == False].iloc[:5]
    
    print("\n室內設施範例:")
    for idx, row in indoor_examples.iterrows():
        print(f"  {row.iloc[6]} ({row.iloc[1]})")
    
    print("\n室外設施範例:")
    for idx, row in outdoor_examples.iterrows():
        print(f"  {row.iloc[6]} ({row.iloc[1]})")
