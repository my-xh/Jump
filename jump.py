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

from PIL import Image
from matplotlib.widgets import Button
from screen_cap import get_screen_image

warnings.filterwarnings('ignore')

if __name__ == '__main__':
    figure = plt.figure()  # 新建空白图形对象
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

    plt.show()
