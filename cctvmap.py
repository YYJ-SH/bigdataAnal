import requests
import xml.etree.ElementTree as ET
import folium

# cctv 위치 좌표 및 정보 리스트
cctv_coords = []
cctv_infos = []

# XML 데이터 스트리밍 처리
url = 'http://openAPI.seoul.go.kr:8088/666d64506c7965613130354f736d664c/xml/safeOpenCCTV_gj/1/999/'
response = requests.get(url, stream=True)

for event, elem in ET.iterparse(response.raw, events=('start', 'end')):
    if event == 'end' and elem.tag == 'row':
        wgsxpt = float(elem.find('WGSXPT').text)
        wgsypt = float(elem.find('WGSYPT').text)
        addr = elem.find('ADDR').text
        qty = elem.find('QTY').text
        cctv_coords.append((wgsxpt, wgsypt))
        cctv_infos.append(f"{addr} ({qty}대)")
        elem.clear()  # 메모리 절약을 위해 요소 제거

# folium 지도 생성 및 마커 추가
seoul_map = folium.Map(location=[37.5665, 126.9780], zoom_start=12)

for coord, info in zip(cctv_coords, cctv_infos):
    folium.Marker(coord, popup=info).add_to(seoul_map)

seoul_map.save('cctv_map.html')