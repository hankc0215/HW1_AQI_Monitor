#!/usr/bin/env python3
"""
AQI 監測網站伺服器
提供動態地圖網站，重新整理後自動更新數據
"""

from flask import Flask, render_template_string, jsonify
import requests
import json
import urllib3
from datetime import datetime
import os

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

class AQIDataFetcher:
    def __init__(self):
        self.api_key = "5a37aebe-f3cb-4aeb-bdae-fd285e2808e2"
        self.base_url = "https://data.moenv.gov.tw/api/v2/AQX_P_432"
        self.taipei_station = (25.0478, 121.5170)
    
    def fetch_aqi_data(self):
        """獲取最新 AQI 數據"""
        params = {
            "api_key": self.api_key,
            "limit": "1000",
            "sort": "ImportDate desc",
            "format": "json"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30, verify=False)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'records' in data:
                return data['records']
            else:
                return []
                
        except Exception as e:
            print(f"獲取數據失敗: {e}")
            return []
    
    def calculate_distance(self, lat, lon):
        """計算到台北車站的距離"""
        import math
        lat1, lon1 = math.radians(lat), math.radians(lon)
        lat2, lon2 = math.radians(self.taipei_station[0]), math.radians(self.taipei_station[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        distance = 6371 * c
        return round(distance, 2)
    
    def get_aqi_color(self, aqi_value):
        """獲取 AQI 對應顏色"""
        try:
            aqi = int(aqi_value)
        except (ValueError, TypeError):
            return '#808080'
        
        if aqi <= 50:
            return '#00E400'  # 綠色
        elif aqi <= 100:
            return '#FFFF00'  # 黃色
        else:
            return '#FF0000'  # 紅色
    
    def get_aqi_level(self, aqi_value):
        """獲取 AQI 等級"""
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

# HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>台灣即時 AQI 監測地圖</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Microsoft JhengHei', Arial, sans-serif;
        }
        #map {
            height: 100vh;
            width: 100%;
        }
        .info-panel {
            position: absolute;
            top: 10px;
            right: 10px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            z-index: 1000;
            max-width: 300px;
        }
        .update-time {
            font-size: 12px;
            color: #666;
            margin-bottom: 10px;
        }
        .stats {
            font-size: 14px;
        }
        .legend {
            margin-top: 10px;
            font-size: 12px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin: 5px 0;
        }
        .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .refresh-btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 10px;
            width: 100%;
        }
        .refresh-btn:hover {
            background: #0056b3;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="info-panel">
        <h3>🌍 台灣 AQI 監測</h3>
        <div class="update-time" id="updateTime">載入中...</div>
        <div class="stats" id="stats">
            <div>總測站數: <span id="totalStations">-</span></div>
            <div>良好: <span id="goodStations">-</span></div>
            <div>普通: <span id="moderateStations">-</span></div>
            <div>不健康: <span id="unhealthyStations">-</span></div>
        </div>
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #00E400;"></div>
                <span>0-50 良好</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FFFF00;"></div>
                <span>51-100 普通</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FF0000;"></div>
                <span>101+ 不健康</span>
            </div>
        </div>
        <button class="refresh-btn" onclick="refreshData()">🔄 重新整理</button>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        let map;
        let markers = [];

        function initMap() {
            map = L.map('map').setView([23.8, 121.0], 7);
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
        }

        function clearMarkers() {
            markers.forEach(marker => map.removeLayer(marker));
            markers = [];
        }

        function createPopupContent(station) {
            return `
                <div style="font-family: Arial, sans-serif; min-width: 200px;">
                    <h4 style="margin: 0 0 10px 0; color: #333;">${station.sitename} 測站</h4>
                    <p style="margin: 5px 0;"><strong>所在地:</strong> ${station.county}</p>
                    <p style="margin: 5px 0;"><strong>即時 AQI:</strong> <span style="font-size: 18px; font-weight: bold; color: ${station.color};">${station.aqi}</span></p>
                    <p style="margin: 5px 0;"><strong>空氣品質:</strong> ${station.level}</p>
                    ${station.pollutant ? `<p style="margin: 5px 0;"><strong>主要污染物:</strong> ${station.pollutant}</p>` : ''}
                    <p style="margin: 5px 0;"><strong>距離台北:</strong> ${station.distance} 公里</p>
                    <p style="margin: 5px 0; font-size: 12px; color: #666;"><strong>更新時間:</strong> ${station.publishtime}</p>
                </div>
            `;
        }

        function updateMap(data) {
            clearMarkers();
            
            data.forEach(station => {
                if (station.latitude && station.longitude) {
                    const marker = L.circleMarker(
                        [station.latitude, station.longitude],
                        {
                            radius: 8,
                            fillColor: station.color,
                            color: 'black',
                            weight: 1,
                            fillOpacity: 0.8
                        }
                    ).addTo(map);
                    
                    marker.bindPopup(createPopupContent(station));
                    marker.bindTooltip(`${station.sitename}: AQI ${station.aqi}`);
                    markers.push(marker);
                }
            });
        }

        function updateStats(data) {
            const stats = {
                total: data.length,
                good: data.filter(s => s.level === '良好').length,
                moderate: data.filter(s => s.level === '普通').length,
                unhealthy: data.filter(s => s.level === '不健康').length
            };

            document.getElementById('totalStations').textContent = stats.total;
            document.getElementById('goodStations').textContent = stats.good;
            document.getElementById('moderateStations').textContent = stats.moderate;
            document.getElementById('unhealthyStations').textContent = stats.unhealthy;
        }

        async function loadData() {
            try {
                const response = await fetch('/api/aqi-data');
                const data = await response.json();
                
                if (data.length > 0) {
                    updateMap(data);
                    updateStats(data);
                    document.getElementById('updateTime').textContent = `最後更新: ${new Date().toLocaleString('zh-TW')}`;
                } else {
                    document.getElementById('updateTime').textContent = '無法獲取數據';
                }
            } catch (error) {
                console.error('載入數據失敗:', error);
                document.getElementById('updateTime').textContent = '載入失敗';
            }
        }

        function refreshData() {
            document.getElementById('updateTime').textContent = '重新整理中...';
            loadData();
        }

        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            initMap();
            loadData();
            
            // 每 5 分鐘自動重新整理
            setInterval(refreshData, 5 * 60 * 1000);
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """主頁面"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/aqi-data')
def api_aqi_data():
    """API 端點：提供 AQI 數據"""
    fetcher = AQIDataFetcher()
    raw_data = fetcher.fetch_aqi_data()
    
    processed_data = []
    for station in raw_data:
        try:
            lat = float(station.get('latitude', 0))
            lon = float(station.get('longitude', 0))
            
            if lat != 0 and lon != 0:
                aqi = station.get('aqi', '')
                processed_station = {
                    'sitename': station.get('sitename', '未知測站'),
                    'county': station.get('county', '未知縣市'),
                    'aqi': aqi,
                    'level': fetcher.get_aqi_level(aqi),
                    'pollutant': station.get('pollutant', ''),
                    'latitude': lat,
                    'longitude': lon,
                    'distance': fetcher.calculate_distance(lat, lon),
                    'color': fetcher.get_aqi_color(aqi),
                    'publishtime': station.get('publishtime', ''),
                    'status': station.get('status', '')
                }
                processed_data.append(processed_station)
        except (ValueError, KeyError):
            continue
    
    return jsonify(processed_data)

if __name__ == '__main__':
    print("🚀 啟動 AQI 監測網站伺服器...")
    print("📱 請在瀏覽器中訪問: http://localhost:5000")
    print("🔄 重新整理頁面即可更新數據")
    print("⏹️  按 Ctrl+C 停止伺服器")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
