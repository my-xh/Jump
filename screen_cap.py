# -*- coding: utf-8 -*-

"""
@File    : screen_cap.py
@Time    : 2021/4/21 21:15
@Author  : my-xh
@Version : 1.0
@Software: PyCharm
@Desc    : 获取手机截图
"""

import os
import subprocess

from PIL import Image

SRC_DIR = '/sdcard/screen.png'
DST_DIR = 'image/screen.png'


def get_screen_image():
    # 截取当前手机界面，并将截图保存到手机sd卡的根目录下
    os.system(f'adb shell screencap -p {SRC_DIR}')
    # 将手机中的截图保存到项目文件夹中
    os.system(f'adb pull {SRC_DIR} {DST_DIR}')

    return Image.open(DST_DIR)


def get_screenshot(img_name):
    """获取手机截图，无返回值"""
    process = subprocess.Popen('adb shell screencap -p', shell=True, stdout=subprocess.PIPE)
    if process is not None:
        # 读取截图信息
        screenshot = process.stdout.read()
        # 计算机识别格式
        binary_screenshot = screenshot.replace(b'\r\n', b'\n')
        # 将图片写入项目文件夹
        with open(img_name, 'wb') as f:
            f.write(binary_screenshot)


if __name__ == '__main__':
    get_screen_image()
