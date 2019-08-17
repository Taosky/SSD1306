# -*- coding: utf-8 -*-
import json
import math
import os
import sys
import time
import config
import requests
import threading
import subprocess
from opts import get_device
from datetime import datetime
from luma.core.render import canvas
from utils import gen_image, font5, font1, font3, font2, weather_now, air_now


def show(my_device):
    def posn(angle, arm_length):
        dx = int(math.cos(math.radians(angle)) * arm_length)
        dy = int(math.sin(math.radians(angle)) * arm_length)
        return dx, dy

    # 模拟时钟
    if config.CLOCK:
        count = 0
        while True:
            count += 1
            if count > 10:
                break

            now = datetime.now()
            today_week = now.strftime("%a")
            with canvas(my_device) as draw:
                now = datetime.now()
                today_date = now.strftime("%d %b")

                margin = 4

                cx = 30
                cy = min(my_device.height, 64) / 2

                left = cx - cy
                right = cx + cy

                hrs_angle = 270 + (30 * (now.hour + (now.minute / 60.0)))
                hrs = posn(hrs_angle, cy - margin - 7)

                min_angle = 270 + (6 * now.minute)
                mins = posn(min_angle, cy - margin - 2)

                sec_angle = 270 + (6 * now.second)
                secs = posn(sec_angle, cy - margin - 2)

                draw.ellipse((left + margin, margin, right - margin, min(my_device.height, 64) - margin),
                             outline="white")
                draw.line((cx, cy, cx + hrs[0], cy + hrs[1]), fill="white")
                draw.line((cx, cy, cx + mins[0], cy + mins[1]), fill="white")
                draw.line((cx, cy, cx + secs[0], cy + secs[1]), fill="red")
                draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill="white", outline="white")
                draw.text((2 * (cx + margin) - 5, cy - 30), today_date, fill="yellow", font=font5)
                draw.text((2 * (cx + margin) + 8, cy), today_week, fill="yellow", font=font5)

            time.sleep(1)

    # 树莓派温度
    with canvas(my_device) as draw:
        draw.text((32, 0), '树莓派', font=font1, fill="white")
        draw.text((20, 21), sensor_data_to_show[0], font=font3, fill="white")
    time.sleep(8)

    # 室温
    if config.ROOM_TEMP:
        with canvas(my_device) as draw:
            draw.text((40, 0), '卧室', font=font1, fill="white")
            draw.text((20, 21), sensor_data_to_show[1], font=font3, fill="white")
        time.sleep(8)

    # 天气情况
    if config.HEWEATHER:
        my_device.display(weather_image_to_show.convert(my_device.mode))
        time.sleep(8)

        # 空气质量
        if config.HEWEATHER_AQI:
            with canvas(my_device) as draw:
                draw.text((6, 12), 'AQI：{}'.format(air_data_to_show[1]), font=font2, fill="white")
            time.sleep(8)


def update_sensor_data():
    print("开启传感器更新线程...")
    global sensor_data_to_show
    while True:
        pi_temp_str = subprocess.check_output(['cat', '/sys/class/thermal/thermal_zone0/temp']).decode('utf-8')
        pi_temp = '{}℃'.format(round(int(pi_temp_str) / 1000, 1))
        room_temp = 0.0
        if config.ROOM_TEMP:
            room_temp_str = \
                subprocess.check_output(['cat', config.ROOM_TEMP_FILE]).decode('utf-8').split(
                    '\n')[1][
                -5:]
            room_temp = '{}℃'.format(round(int(room_temp_str) / 1000, 1))

        sensor_data_to_show = pi_temp, room_temp

        # 休眠
        time.sleep(120)


# 生成天气图像及空气质量数据
def update_weather_data(dev_size):
    print("开启更新天气线程...")
    global weather_image_to_show
    global air_data_to_show
    while True:
        # 天气
        code, text, temp = weather_now()
        weather_image_to_show = gen_image(code, temp, dev_size)

        # 空气
        air_data_to_show = air_now()

        # 休眠
        time.sleep(1200)


def update_internet_status():
    print('开启网络检测线程...')
    global internet_on
    while True:
        try:
            r = requests.get('https://www.baidu.com')
            if r.status_code == 200:
                internet_on = True
            else:
                internet_on = False
        except Exception:
            internet_on = False
        time.sleep(600)


def main():
    global air_data_to_show
    air_data_to_show = ('无', '-1')
    global sensor_data_to_show
    sensor_data_to_show = ('-1', '-1')
    global internet_on
    internet_on = False

    global weather_image_to_show
    weather_image_to_show = gen_image(999, '错误', device.size)

    t1 = threading.Thread(target=update_sensor_data, daemon=True)
    t1.start()
    t2 = threading.Thread(target=update_weather_data, daemon=True, args=(device.size,))
    t2.start()
    t3 = threading.Thread(target=update_internet_status, daemon=True)
    t3.start()

    # 设定亮度
    device.contrast(1)
    # 执行
    time.sleep(5)
    while True:
        device.hide()
        device.show()
        # if internet_on:
        show(device)


if __name__ == "__main__":
    if os.name != 'posix':
        sys.exit('{} platform not supported'.format(os.name))
    try:
        device = get_device()  # 获取并输出设备信息 _opts.get_device()
        main()
    except KeyboardInterrupt:  # ctrl+c退出
        pass
