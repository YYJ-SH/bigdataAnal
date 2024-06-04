import json

# GeoJSON 파일 읽기
with open('Dong.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

# GeoJSON 데이터 파싱
for feature in geojson_data['features']:
    properties = feature.get('properties', {})
    print(properties)