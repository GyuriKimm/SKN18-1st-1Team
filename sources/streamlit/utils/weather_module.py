import datetime
import requests

API_KEY = "HZXgpAiQBEp9H9gcEzePi/qvWpMqa2Vav8W9Jaounr+S2hvMRYMdBlOqdWrVp81amfnm6W0B1IhPD+t9DyQAfQ=="
# 날씨 API 호출 함수
def get_weather():
    now = datetime.datetime.now()
    base_date = now.strftime('%Y%m%d')
    base_time = (now - datetime.timedelta(hours=1)).strftime('%H') + "00"
    nx, ny = 58, 125  # 서울 금천구

    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'
    params = {
        'serviceKey': API_KEY,
        'pageNo': '1',
        'numOfRows': '1000',
        'dataType': 'JSON',
        'base_date': base_date,
        'base_time': base_time,
        'nx': nx,
        'ny': ny
    }

    response = requests.get(url, params=params)
    items = response.json().get('response', {}).get('body', {}).get('items', {}).get('item', [])
    data = {}

    for item in items:
        cat = item.get('category')
        val = item.get('obsrValue')
        if cat == 'T1H':
            data['기온'] = f"{val}°C"
        elif cat == 'REH':
            data['습도'] = f"{val}%"
        elif cat == 'WSD':
            data['풍속'] = f"{val} m/s"
        elif cat == 'RN1':
            data['강수량'] = f"{val} mm"

    return data