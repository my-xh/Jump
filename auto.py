# -*- coding: utf-8 -*-

"""
@File    : auto.py
@Time    : 2021/4/22 8:25
@Author  : my-xh
@Version : 1.0
@Software: PyCharm
@Desc    : 自动模式
"""

import threading
import time
import os

from PIL import Image
from screen_cap import get_screenshot
from random import randint


class StopAutoMode(Exception):
    """自动模式停止标志"""


class AutoMode(threading.Thread):
    """自动模式"""

    def __init__(self, callback_update, callback_stop):
        super().__init__()
        self.daemon = True  # 设置为守护线程
        self.image_path = 'image/auto_jump.png'  # 自动模式截图保存路径
        self.__callback_update = callback_update
        self.__callback_stop = callback_stop

    def run(self):
        times = int(input('请输入自动跳跃次数: '))

        for i in range(times):
            get_screenshot(self.image_path)  # 执行手机截图并保存到项目文件夹下
            img = Image.open(self.image_path)  # 读取截图文件

            try:
                self.auto_jump(img)
                print(f'自动跳{i + 1}次')
            except StopAutoMode as e:
                print(e)
                break

            time.sleep(2)
            if callable(self.__callback_update):
                self.__callback_update()  # 更新主窗体

        if callable(self.__callback_stop):
            self.__callback_stop()  # 停止自动模式

    def auto_jump(self, img):
        """自动跳跃"""
        self.width, self.height = img.size
        self.pixels = img.load()  # 获得图片像素矩阵
        self.scan_side_x = int(self.width / 8)  # x轴扫描边界
        self.scan_side_y = int(self.height / 3)  # y轴扫描边界

        if sum(self.pixels[5, 5][:3]) < 150:
            raise StopAutoMode('\033[1;31m检测到手机锁屏，已停止自动模式\033[0m')

        # 第一步，以50px为单位，从下往上快速扫描图片找到第一个棋盘的位置，确定y轴扫描的起点
        # 第二步，从y轴扫描起点开始进行详细扫描，根据棋子的特殊颜色找到棋子最后一行像素点的中心点，作为跳跃起点
        # 第三步，通过棋子底部中心确定棋盘的范围，通过色差找到棋盘并获取棋盘横向坐标的中心点，作为跳跃终点
        # 第四步，根据跳跃起点和终点的水平距离和手机屏幕宽度计算棋子跳跃百分比，进而得到屏幕按压时长
        self.__get_start_y()
        self.__get_piece_x()
        self.__get_board_x()
        self.__jump()

    def __get_start_y(self):
        """获取y轴的扫描起点"""
        self.scan_start_y = 0
        start_x, end_x = self.scan_side_x, self.width - self.scan_side_x
        start_y, end_y = self.height - self.scan_side_y, self.scan_side_y

        for y in range(start_y, end_y, -50):
            first_pixel = self.pixels[0, y]
            for x in range(start_x, end_x, 5):
                pixel = self.pixels[x, y]
                if pixel != first_pixel:
                    self.scan_start_y = y + 50
                    # print(f'从y={self.scan_start_y}开始扫描')
                    return

    def __get_piece_x(self):
        """获取棋子底部中心点横坐标"""
        self.piece_x = 0
        piece_start_x, piece_end_x = self.scan_side_x, self.width - self.scan_side_x
        piece_start_y, piece_end_y = self.scan_start_y, self.scan_side_y

        for y in range(piece_start_y, piece_end_y, -1):
            find_left = False  # 是否找到了棋子一行像素的最左端
            for x in range(piece_start_x, piece_end_x):
                r, g, b = self.pixels[x, y][:3]

                # 如果不是棋子颜色，则继续检测下一个像素
                if r not in range(50, 60) or (
                        g not in range(53, 63) or b not in range(95, 110)):
                    continue

                # 如果是棋子颜色，先确定最左端，再确定最右端，最终得到棋子底部中心
                if not find_left:
                    left = x
                    find_left = True
                else:
                    right = x
                    self.piece_x = int((left + right) / 2)
                    # print(f'棋子底部中心点: {self.piece_x}, {y}')
                    return

    def __get_board_x(self):
        """获取棋盘中心点横坐标"""
        self.board_x = 0
        width, height = self.width, self.height
        if self.piece_x < width // 2:
            board_start_x, board_end_x = width // 2, width - self.scan_side_x
        else:
            board_start_x, board_end_x = self.scan_side_x, width // 2
        board_start_y, board_end_y = (height - width) // 2, (height + width) // 2

        board_x_set = []  # 使用列表避免去重
        for y in range(board_start_y, board_end_y, 5):
            bg_r, bg_g, bg_b = self.pixels[0, y][:3]  # 获取背景像素值
            for x in range(board_start_x, board_end_x):
                r, g, b = pixel = self.pixels[x, y][:3]

                # 色差比较
                if abs(r - bg_r) + abs(g - bg_g) + abs(b - bg_b) < 10:
                    continue
                board_x_set.append(x)

            if len(board_x_set) > 10:
                self.board_x = sum(board_x_set) // len(board_x_set)
                # print(f'棋盘中心点横坐标: {self.board_x}')
                return

    def __jump(self):
        """具体的跳跃方法"""
        distance_x = abs(self.piece_x - self.board_x)  # 起点到终点的水平距离
        jump_percent = distance_x / self.width  # 跳跃百分比
        jump_fill_width = 1750  # 跳过整个宽度需要按压的毫秒数
        duration = max(int(jump_fill_width * jump_percent), 200)  # 计算需要按压的毫秒数

        # 随机生成按压点
        point1_x = randint(815, 923)
        point1_y = randint(1509, 1658)
        point2_x = point1_x + randint(0, 3)
        point2_y = point1_y + randint(0, 3)

        # 按压命令
        cmd = f'adb shell input swipe {point1_x} {point1_y} {point2_x} {point2_y} {duration}'

        os.system(cmd)


class AutoManager:
    """自动模式管理器"""

    def __init__(self, callback_update):
        self.is_auto = False  # 自动模式开关
        self.__callback_update = callback_update  # 主窗体更新方法

    def __call__(self, event):
        if self.is_auto:
            # print('不要重复开启自动模式！')
            return

        print('\033[1;32m自动模式已开启\033[0m')
        self.is_auto = True  # 开启自动模式
        auto_mode = AutoMode(self.__callback_update, self.__callback_stop)
        auto_mode.start()  # 启动自动模式线程

    def __bool__(self):
        return self.is_auto

    def __callback_stop(self):
        """自动模式线程完成后的回调方法"""
        self.is_auto = False  # 关闭自动模式
        print('\033[1;31m自动模式已结束\033[0m')
