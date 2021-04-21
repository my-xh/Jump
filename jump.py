# -*- coding: utf-8 -*-

"""
@File    : jump.py
@Time    : 2021/4/21 20:16
@Author  : my-xh
@Version : 1.0
@Software: PyCharm
@Desc    : 
"""

import matplotlib.pyplot as plt
import warnings
import os
import time
import numpy

from PIL import Image
from matplotlib.widgets import Button
from screen_cap import get_screen_image
from threading import Thread

warnings.filterwarnings('ignore')


def jump_to_next(point1, point2):
    """实现跳跃的方法"""
    x1, y1 = point1
    x2, y2 = point2
    distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    # 执行按压手机屏幕的命令，每个像素1.35毫秒
    os.system(f'adb shell input swipe 550 1550 550 1550 {int(distance * 1.35)}')
    print('跳')


def update():
    """更新主窗体画面"""
    time.sleep(0.8)
    print('更新')

    # 重新获取手机截图并显示
    axes_image.set_data(numpy.array(get_screen_image()))
    figure.canvas.draw()


def on_click(event):
    if is_auto:
        print('已开启自动模式！')
    else:
        x, y = event.xdata, event.ydata
        # 当鼠标点击图片外面或者重选、自动按钮时不做任何处理
        if x is None or y is None or not isinstance(event.inaxes, plt.Subplot):
            return

        x, y = float(x), float(y)
        coor.append((x, y))

        axes.plot(x, y, 'r*')  # 绘制红色的*号
        figure.canvas.draw()  # 重画

        if len(coor) == 2:
            jump_to_next(coor.pop(), coor.pop())  # 执行跳跃方法，并清空选取坐标
            axes.lines.clear()  # 清除绘制的红色*号
            Thread(target=update).start()  # 通过线程执行主界面更新


if __name__ == '__main__':
    coor = []  # 保存选取位置的坐标
    is_auto = False  # 自动模式标记
    figure = plt.figure()  # 新建空白图形对象
    axes = figure.add_subplot(1, 1, 1)  # 创建用于绘制选取位置的子视图

    # 将获取的图片显示在主窗体中
    axes_image = plt.imshow(get_screen_image(), animated=True)

    # 添加重选按钮
    reselect_position = plt.axes([0.79, 0.8, 0.1, 0.08])
    reselect_image = Image.open('image/bt.png')
    reselect_button = Button(reselect_position, label='', image=reselect_image)

    # 添加自动按钮
    auto_position = plt.axes([0.79, 0.65, 0.1, 0.08])
    auto_image = Image.open('image/bt1.png')
    auto_button = Button(auto_position, label='', image=auto_image)

    # 设置主窗体单击事件
    figure.canvas.mpl_connect('button_press_event', on_click)

    plt.show()
