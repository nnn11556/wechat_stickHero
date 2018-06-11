# encoding: utf-8
"""
@author: nnn11556
@software: PyCharm
@file: stick_hero.py
@time: 2018/6/8 23:36
"""
import os
import cv2
import numpy as np
import time

#一些常量定义
imgPath = 'screenshoot.png'
#屏幕纵横像素
HEIGHT = 1920
WIDTH = 1080

bx1 = WIDTH / 2
bx2 = WIDTH / 2
by1 = HEIGHT / 2
by2 = HEIGHT / 2

#蒙版阈值
lower = np.array([35, 60, 130])
upper = np.array([50, 70, 140])

#点击时间参数，控制按压时间
alpha = 1.16

#使用adb指令获取手机屏幕截图
def pull_screenshot(path):
    os.system('adb shell screencap -p /sdcard/%s' % path)
    os.system('adb pull /sdcard/%s .' % path)

# 保存失败时的图片 用于DEBUG
def saveBugImg():
    index = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
    path = os.path.abspath('.')
    img1 = cv2.imread('raw.png')
    path1 = path + '\\test\\' + index +'raw.png'
    cv2.imwrite(path1, img1)
    img2 = cv2.imread('result.png')
    path2 = path + '\\test\\' + index +'result.png'
    cv2.imwrite(path2, img2)

'''
思路   实际上这个游戏比跳一跳还要简单一些，移动的目标中心是一个红点区域，直接识别这个红点区域
       就行了，找到像素值为[0,0,204]的区域，就找到了目标区域的x轴坐标。对于小人的检测，还是借
       鉴跳一跳中对棋子的识别，使用外接圆来识别小人的头发区域，效果还行吧。最高能到4000多分，
       普遍在1500分左右。
'''
def handle_img(path):
    img_cv = cv2.imread(path)
    #找到目标的位置x坐标
    start_index = 0
    count = 0
    #忽略左侧小人脚下的红点
    for index, px in enumerate(img_cv[int(0.72*HEIGHT), int(0.1*WIDTH):]):
        if px[0] == 0 and px[1] == 0 and px[2] == 204:  # red
            if count == 0:
                start_index = index+int(0.1*WIDTH)
            count += 1
    target_x = int((start_index + count / 2))
    #找到小人的位置x坐标
    mask = cv2.inRange(img_cv, lower, upper)  # 建立蒙版
    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]  # 找到轮廓
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)  # 找到面积最大的轮廓
    ((x, y), radius) = cv2.minEnclosingCircle(c)  # 确定面积最大的轮廓的外接圆
    center = (int(x), int(y))
    character_x = int(x)
    # if DEBUG:
    #保存检测结果
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    gray[:, target_x - 2:target_x + 2] = 255
    gray[:, character_x - 2:character_x + 2] = 255
    cv2.circle(gray, center, int(radius + 10), (255, 255, 255), 3)  # 画出圆心
    cv2.circle(gray, center, 3, (0, 0, 255), -1)
    cv2.imwrite('result.png', gray)
    cv2.imwrite('raw.png', img_cv)
    # cv2.destroyAllWindows()  # 显示检测结果
    # cv2.namedWindow("Result", flags=cv2.WINDOW_KEEPRATIO)
    # cv2.resizeWindow("Result",360,640)
    # cv2.imshow("Result", gray)
    # cv2.waitKey(1000)
    return target_x, character_x

# 小人移动,计算两点间距离换算成按压时间
def move(x1,x2):
    distance = x1 - x2
    press_time = int(distance * alpha)
    cmd = 'adb shell input swipe {} {} {} {} {}'.format(bx1, by1, bx2, by2, press_time)
    os.system(cmd)

def main():
    cheak = input('请确保手机已打开USB调试并连接电脑[y/n]:')
    while True:
        if cheak.lower() == 'y':
            break
    times = 0
    while True:
        try:
            pull_screenshot(imgPath)
            x1, x2 = handle_img(imgPath)
            move(x1, x2)
            times += 1
            print('第%d次' % times)
            # 等待小人走完
            time.sleep(4.5 + np.random.rand())
        except:
            saveBugImg()
            break
    cv2.waitKey(0)
if __name__ == '__main__':
    main()