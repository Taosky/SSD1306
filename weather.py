# coding:utf-8
from config import HEWEATHER_CITY, HEWEATHER_KEY
import requests
import json


def weather_now():
    try:
        r = requests.get(
            'https://free-api.heweather.net/s6/weather/now?location={}&key={}'.format(HEWEATHER_CITY, HEWEATHER_KEY))
        result = json.loads(r.text)
        weather = result['HeWeather6'][0]['now']
    except Exception as e:
        print(e)
        return '999', '出错', '--'
    return weather['cond_code'], weather['cond_txt'], weather['tmp']


def air_now():
    try:
        r = requests.get(
            'https://free-api.heweather.net/s6/air/now?location={}&key={}'.format(HEWEATHER_CITY, HEWEATHER_KEY))
        result = json.loads(r.text)
        air = result['HeWeather6'][0]['air_now_city']
    except Exception as e:
        print(e)
        return '错误', '-1'
    return air['qlty'], air['aqi']
