import json
import os
import time

import requests
from PIL import Image, ImageOps, ImageDraw, ImageFont

# 自定义字体
from config import HEWEATHER_CITY, HEWEATHER_KEY

font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fonts', 'code2000.ttf'))  # 导入字体文件
font1 = ImageFont.truetype(font_path, 21)  # 小标题
font2 = ImageFont.truetype(font_path, 30)  # 天气文字
font3 = ImageFont.truetype(font_path, 34)  # 传感器温度
font5 = ImageFont.truetype(font_path, 19)  # 日期和周数


def gen_image(cond_code, tmp, device_size):
    icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             'weather_icon', '{}.jpg'.format(cond_code)))
    weather_icon = Image.open(icon_path)
    inverted_icon = ImageOps.invert(weather_icon).convert("RGBA")
    weather_image = Image.new("RGBA", device_size)
    weather_image.paste(inverted_icon, (0, 0))
    draw = ImageDraw.Draw(weather_image)
    draw.text((66, 12), '{}℃'.format(tmp), (255, 255, 255), font=font2)
    return weather_image


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
