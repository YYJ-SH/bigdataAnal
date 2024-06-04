import requests
from xml.etree import ElementTree as ET
from pyproj import Proj, transform
import folium
import warnings

# 경고 메시지 필터링
warnings.filterwarnings('ignore', category=FutureWarning)

# 대규모점포 데이터 파싱
url_store = "http://openapi.seoul.go.kr:8088/666d64506c7965613130354f736d664c/xml/LOCALDATA_082501_GJ/1/100/"
response_store = requests.get(url_store)
root_store = ET.fromstring(response_store.content)

url_park = "http://openapi.seoul.go.kr:8088/666d64506c7965613130354f736d664c/xml/LOCALDATA_030712_GJ/1/999/"
response_park = requests.get(url_park)
root_park = ET.fromstring(response_park.content)

# TM 좌표계 정의 (EPSG:2097 - TM중부원점)
tm_proj = Proj(init='epsg:2097')

# WGS84 좌표계 정의 (EPSG:4326 - 위도, 경도)
wgs84_proj = Proj(init='epsg:4326')

store_names = []
store_coords = []

for row in root_store.iter("row"):
    bplcnm = row.find("BPLCNM").text
    x_elem = row.find("X")
    y_elem = row.find("Y")

    if x_elem is not None and y_elem is not None:
        x_text = x_elem.text.strip() if x_elem.text else None
        y_text = y_elem.text.strip() if y_elem.text else None

        if x_text and y_text:
            try:
                x = float(x_text)
                y = float(y_text)

                # TM 좌표를 위도, 경도로 변환
                lon, lat = transform(tm_proj, wgs84_proj, x, y)

                store_names.append(bplcnm)
                store_coords.append((lat, lon))
            except ValueError:
                print(f"잘못된 좌표 값: {bplcnm}")
        else:
            print(f"좌표 값 없음: {bplcnm}")
    else:
        print(f"좌표 태그 없음: {bplcnm}")

# 광진구 중심 좌표
center_lat = 37.538621
center_lng = 127.082841

# Folium 지도 생성
m = folium.Map(location=[center_lat, center_lng], zoom_start=13)

# 대규모점포 마커 추가 (빨간색)
for name, coord in zip(store_names, store_coords):
    folium.Marker(coord, popup=name, icon=folium.Icon(color="red")).add_to(m)

# 지도 저장
m.save("gwangjin_store_map.html")