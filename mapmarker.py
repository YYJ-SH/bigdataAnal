import requests
import folium
import pandas as pd
from xml.etree import ElementTree as ET

# 대규모점포 데이터 파싱
url_store = "http://openapi.seoul.go.kr:8088/666d64506c7965613130354f736d664c/xml/LOCALDATA_082501_GJ/1/100/"
response_store = requests.get(url_store)
root_store = ET.fromstring(response_store.text)

store_data = []
for row in root_store.iter("row"):
    try:
        store = {
            "name": row.find("BPLCNM").text,
            "x": float(row.find("X").text),
            "y": float(row.find("Y").text)
        }
        store_data.append(store)
    except AttributeError:
        continue

# 종합유원시설 데이터 파싱
url_park = "http://openapi.seoul.go.kr:8088/666d64506c7965613130354f736d664c/xml/LOCALDATA_030712_GJ/1/999/"
response_park = requests.get(url_park)
root_park = ET.fromstring(response_park.text)

park_data = []
for row in root_park.iter("row"):
    if row.find("DTLSTATENM").text != "허가취소":
        try:
            park = {
                "name": row.find("BPLCNM").text,
                "x": float(row.find("X").text),
                "y": float(row.find("Y").text)
            }
            park_data.append(park)
        except AttributeError:
            continue

# 공연장 데이터 파싱
url_theater = "http://openapi.seoul.go.kr:8088/666d64506c7965613130354f736d664c/xml/LOCALDATA_030601_GJ/1/300/"
response_theater = requests.get(url_theater)
root_theater = ET.fromstring(response_theater.text)

theater_data = []
for row in root_theater.iter("row"):
    try:
        theater = {
            "name": row.find("BPLCNM").text,
            "x": float(row.find("X").text),
            "y": float(row.find("Y").text)
        }
        theater_data.append(theater)
    except AttributeError:
        continue

# 광진구 중심 좌표
center_lat = 37.538621
center_lng = 127.082841

# Folium 지도 생성
m = folium.Map(location=[center_lat, center_lng], zoom_start=13)

# 대규모점포 마커 추가 (빨간색)
for store in store_data:
    folium.Marker([store["y"], store["x"]], popup=store["name"], icon=folium.Icon(color="red")).add_to(m)

# 종합유원시설 마커 추가 (파란색)
for park in park_data:
    folium.Marker([park["y"], park["x"]], popup=park["name"], icon=folium.Icon(color="blue")).add_to(m)

# 공연장 마커 추가 (초록색)
for theater in theater_data:
    folium.Marker([theater["y"], theater["x"]], popup=theater["name"], icon=folium.Icon(color="green")).add_to(m)

# 지도 저장
m.save("gwangjin_map.html")