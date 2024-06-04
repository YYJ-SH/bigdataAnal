import requests
from xml.etree import ElementTree as ET
from pyproj import Proj, transform
import folium
import warnings
import pandas as pd
from sklearn.cluster import DBSCAN

# 경고 메시지 필터링
warnings.filterwarnings('ignore', category=FutureWarning)

# XML 데이터 파싱
def parse_xml(xml_string):
   root = ET.fromstring(xml_string)
   data = []
   for elem in root.findall('.//row'):
       tags = ['BPLCNM', 'X', 'Y']
       item = {}
       for tag in tags:
           tag_elem = elem.find(tag)
           item[tag] = tag_elem.text.strip() if tag_elem is not None and tag_elem.text else None
       data.append(item)
   return pd.DataFrame(data)

# URL과 마커 색상 정보
url_color_info = [
   ('http://openapi.seoul.go.kr:8088/666d64506c7965613130354f736d664c/xml/LOCALDATA_082501_GJ/1/400/', 'blue'),
   ('http://openapi.seoul.go.kr:8088/666d64506c7965613130354f736d664c/xml/LOCALDATA_030712_GJ/1/999/', 'red'),
   ('http://openapi.seoul.go.kr:8088/666d64506c7965613130354f736d664c/xml/LOCALDATA_030709_GJ/1/400/', 'green'),
   ('http://openapi.seoul.go.kr:8088/666d64506c7965613130354f736d664c/xml/LOCALDATA_030601_GJ/1/400/', 'pink'),
   ('http://openapi.seoul.go.kr:8088/666d64506c7965613130354f736d664c/xml/LOCALDATA_030602_GJ/1/400/', 'black')
]

# TM 좌표계 정의 (EPSG:2097 - TM중부원점)
tm_proj = Proj(init='epsg:2097')

# WGS84 좌표계 정의 (EPSG:4326 - 위도, 경도)
wgs84_proj = Proj(init='epsg:4326')

# folium 지도 생성
seoul_map = folium.Map(location=[37.5665, 126.9780], zoom_start=12)

all_coords = []
all_names = []

for url, color in url_color_info:
   # URL을 통해 XML 데이터 가져오기
   response = requests.get(url)
   xml_data = response.content
   
   # XML 데이터 파싱
   df = parse_xml(xml_data)
   
   # 좌표 변환 및 점포명 추출
   coords = []
   names = []
   for _, row in df.iterrows():
       if pd.notna(row['X']) and pd.notna(row['Y']):
           try:
               x, y = transform(tm_proj, wgs84_proj, float(row['X']), float(row['Y']))
               coords.append([y, x])
               names.append(row['BPLCNM'])
           except ValueError:
               print(f"좌표 값 오류: {row['X']}, {row['Y']}")
   
   all_coords.extend(coords)
   all_names.extend(names)

# 마커 추가
for coord, name in zip(all_coords, all_names):
   folium.Marker(location=coord, popup=name, icon=folium.Icon(color='blue', icon='info-sign')).add_to(seoul_map)

# DBSCAN 클러스터링
dbscan = DBSCAN(eps=0.005, min_samples=5)  # eps는 클러스터링 범위, min_samples는 클러스터를 형성하기 위한 최소 샘플 수
clusters = dbscan.fit_predict(all_coords)

# 클러스터 테두리 그리기
for cluster_id in set(clusters):
   if cluster_id != -1:  # -1은 노이즈 포인트를 의미
       cluster_coords = [coord for coord, c_id in zip(all_coords, clusters) if c_id == cluster_id]
       folium.Polygon(locations=cluster_coords, color='red', fill=False, weight=2).add_to(seoul_map)

# 지도 저장
seoul_map.save('combined_large_stores_map_with_clusters.html')