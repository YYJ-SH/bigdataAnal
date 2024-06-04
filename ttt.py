# CCTV 데이터 수집
import requests
import xml.etree.ElementTree as ET
import folium
from pyproj import Proj, transform
from sklearn.cluster import DBSCAN
from scipy.spatial import ConvexHull
import numpy as np
import warnings



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
                    print(f"CCTV 추가: {addr} ({qty}대)")  # 디버깅 메시지 추가
                except ValueError:
                    print(f"Invalid coordinates: {wgsxpt_text}, {wgsypt_text}")
            else:
                print("Missing coordinate values for CCTV")
        else:
            print("Missing coordinate elements for CCTV")
        
        elem.clear()

print(f"수집된 CCTV 데이터 개수: {len(cctv_coords)}")  # 디버깅 메시지 추가