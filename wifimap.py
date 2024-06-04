import requests
import xml.etree.ElementTree as ET
import folium

# 실외 위치 좌표 및 와이파이 명칭 리스트
outdoor_coords = []
outdoor_names = []

# XML 데이터 스트리밍 처리
url = 'http://openapi.seoul.go.kr:8088/666d64506c7965613130354f736d664c/xml/TbPublicWifiInfo_GJ/1/999/'
response = requests.get(url, stream=True)

for event, elem in ET.iterparse(response.raw, events=('start', 'end')):
    if event == 'end' and elem.tag == 'row':
        x_swifi_inout_door = elem.find('X_SWIFI_INOUT_DOOR').text
        if x_swifi_inout_door == '실외':
            lat = float(elem.find('LAT').text)
            lnt = float(elem.find('LNT').text)
            name = elem.find('X_SWIFI_MAIN_NM').text
            outdoor_coords.append((lat, lnt))
            outdoor_names.append(name)
        elem.clear()  # 메모리 절약을 위해 요소 제거

# folium 지도 생성 및 마커 추가
seoul_map = folium.Map(location=[37.5665, 126.9780], zoom_start=12)

for coord, name in zip(outdoor_coords, outdoor_names):
    folium.Marker(coord, popup=name).add_to(seoul_map)

seoul_map.save('wifi_map.html')