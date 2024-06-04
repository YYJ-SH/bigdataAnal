import requests
import xml.etree.ElementTree as ET
import folium
from pyproj import Proj, transform
from sklearn.cluster import DBSCAN
from scipy.spatial import ConvexHull
import numpy as np
import warnings

# FutureWarning 메시지 필터링
warnings.filterwarnings('ignore', category=FutureWarning)

# 인구 밀집 지역 데이터 수집
url_color_info = [
    ('http://openapi.seoul.go.kr:8088/666d64506c7965613130354f736d664c/xml/LOCALDATA_082501_GJ/1/400/', 'blue'),
    ('http://openapi.seoul.go.kr:8088/666d64506c7965613130354f736d664c/xml/LOCALDATA_030712_GJ/1/999/', 'red'),
    ('http://openapi.seoul.go.kr:8088/666d64506c7965613130354f736d664c/xml/LOCALDATA_030709_GJ/1/400/', 'green'),
    ('http://openapi.seoul.go.kr:8088/666d64506c7965613130354f736d664c/xml/LOCALDATA_030601_GJ/1/400/', 'pink'),
    ('http://openapi.seoul.go.kr:8088/666d64506c7965613130354f736d664c/xml/LOCALDATA_030602_GJ/1/400/', 'black')
]

tm_proj = Proj(init='epsg:2097')
wgs84_proj = Proj(init='epsg:4326')

coords = []
names = []
colors = []

for url, color in url_color_info:
    response = requests.get(url)
    root = ET.fromstring(response.content)
    
    for row in root.iter("row"):
        name = row.find("BPLCNM").text
        x_elem = row.find("X")
        y_elem = row.find("Y")
        
        if x_elem is not None and y_elem is not None:
            x_text = x_elem.text
            y_text = y_elem.text
            if x_text is not None and y_text is not None:
                try:
                    x = float(x_text)
                    y = float(y_text)
                    x, y = transform(tm_proj, wgs84_proj, x, y)
                    coords.append((y, x))
                    names.append(name)
                    colors.append(color)
                except ValueError:
                    print(f"Invalid coordinates for {name}: {x_text}, {y_text}")
            else:
                print(f"Missing coordinates for {name}")
        else:
            print(f"Missing coordinate elements for {name}")

# CCTV 데이터 수집
cctv_coords = []
cctv_infos = []

url = 'http://openAPI.seoul.go.kr:8088/666d64506c7965613130354f736d664c/xml/safeOpenCCTV_gj/1/999/'
response = requests.get(url, stream=True)
for event, elem in ET.iterparse(response.raw, events=('start', 'end')):
    if event == 'end' and elem.tag == 'row':
        wgsxpt_elem = elem.find('WGSXPT')
        wgsypt_elem = elem.find('WGSYPT')
        addr_elem = elem.find('ADDR')
        qty_elem = elem.find('QTY')
        
        if wgsxpt_elem is not None and wgsypt_elem is not None:
            wgsxpt_text = wgsxpt_elem.text
            wgsypt_text = wgsypt_elem.text
            if wgsxpt_text is not None and wgsypt_text is not None:
                try:
                    wgsxpt = float(wgsxpt_text)
                    wgsypt = float(wgsypt_text)
                    addr = addr_elem.text if addr_elem is not None else "N/A"
                    qty = qty_elem.text if qty_elem is not None else "N/A"
                    cctv_coords.append((wgsypt, wgsxpt))
                    cctv_infos.append(f"{addr} ({qty}대)")
                except ValueError:
                    print(f"Invalid coordinates: {wgsxpt_text}, {wgsypt_text}")
            else:
                print("Missing coordinate values for CCTV")
        else:
            print("Missing coordinate elements for CCTV")
        
        elem.clear()

# 인구 밀집 지역과 CCTV 데이터 통합
all_coords = coords + cctv_coords
all_names = names + ['CCTV'] * len(cctv_coords)
all_colors = colors + ['lightblue'] * len(cctv_coords)

# 클러스터링
dbscan = DBSCAN(eps=0.005, min_samples=5)
clusters = dbscan.fit_predict(all_coords)

unique_clusters = set(clusters)

# 지도 시각화
map_osm = folium.Map(location=[37.5665, 126.9780], zoom_start=12)

for coord, name, color in zip(all_coords, all_names, all_colors):
    folium.Marker(location=coord, popup=name, icon=folium.Icon(color=color)).add_to(map_osm)

for cluster_id in unique_clusters:
    if cluster_id != -1:
        cluster_coords = [coord for coord, c_id in zip(all_coords, clusters) if c_id == cluster_id]
        if len(cluster_coords) >= 3:
            cluster_coords = np.unique(np.array(cluster_coords), axis=0)
            if len(cluster_coords) >= 3:
                cluster_coords += np.random.normal(0, 1e-6, size=cluster_coords.shape)
                hull = ConvexHull(cluster_coords)
                hull_coords = [cluster_coords[vertex] for vertex in hull.vertices]
                folium.Polygon(locations=hull_coords, color='red', fill=True, fill_color='red', fill_opacity=0.3).add_to(map_osm)

map_osm.save('seoul_danger_zones.html')