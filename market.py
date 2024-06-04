import requests
import folium
from xml.etree import ElementTree as ET

# 대규모점포 데이터 파싱
url_store = "http://openapi.seoul.go.kr:8088/666d64506c7965613130354f736d664c/xml/LOCALDATA_082501_GJ/1/100/"
response_store = requests.get(url_store)

store_names = []
store_coords = []
root_store = ET.fromstring(response_store.content)
for row in root_store.iter("row"):
    store_names.append(row.find("BPLCNM").text)
    x = row.find("X")
    y = row.find("Y")
    if x is not None and y is not None:
        x_text = x.text.strip() if x.text else None
        y_text = y.text.strip() if y.text else None
        if x_text and y_text:
            store_coords.append((float(y_text), float(x_text)))

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