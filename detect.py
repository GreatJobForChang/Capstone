import os

import cv2
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import pyautogui
import datetime
from PIL import ImageGrab

# 设定监听键盘初始状态
f = open('keylogger.txt', 'w')
f.write('False')
f.close()

g = open('endflag.txt', 'w')
g.write('False')
g.close()

auto = True  # 1. determine if cursor has moved to the position of head
os.system("mkdir output")  # 创建output目录


def write_out_file(outfilename, frame):
    cv.imwrite(outfilename, frame)


total_frame = 378

thr = 0.2
width = 160
height = 160

BODY_PARTS = {"Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
              "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
              "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
              "LEye": 15, "REar": 16, "LEar": 17, "Background": 18}

POSE_PAIRS = [["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
              ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
              ["Neck", "RHip"], ["RHip", "RKnee"], [
                  "RKnee", "RAnkle"], ["Neck", "LHip"],
              ["LHip", "LKnee"], ["LKnee", "LAnkle"], [
                  "Neck", "Nose"], ["Nose", "REye"],
              ["REye", "REar"], ["Nose", "LEye"], ["LEye", "LEar"]]

inWidth = width
inHeight = height

net = cv.dnn.readNetFromTensorflow("graph_opt.pb")
#net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
#net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)
name = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
# get the size of screen and used to adjust
fourcc = cv.VideoWriter_fourcc(*'XVID')
video = cv.VideoWriter('test_%s.avi'%name, fourcc, 20, (640, 480))
isSave = False

while True:
    flag = open('keylogger.txt', 'r').read()
    if flag == 'True':
        # 自动截屏
        im = ImageGrab.grab((640, 300, 1280, 780))
        im.save('path-to-save.png')
        img = cv2.imread(r'path-to-save.png')
        # print(type(img))
        frame = img

        frameWidth = frame.shape[1]
        frameHeight = frame.shape[0]

        net.setInput(cv.dnn.blobFromImage(frame, 1.0, (inWidth, inHeight),
                                          (127.5, 127.5, 127.5), swapRB=True, crop=True))
        out = net.forward()
        # MobileNet output [1, 57, -1, -1], we only need the first 19 elements
        out = out[:, :19, :, :]

        assert (len(BODY_PARTS) == out.shape[1])

        points = []
        for i in range(len(BODY_PARTS)):
            heatMap = out[0, i, :, :]

            _, conf, _, point = cv.minMaxLoc(heatMap)
            x = (frameWidth * point[0]) / out.shape[3]
            y = (frameHeight * point[1]) / out.shape[2]
            # Add a point if it's confidence is higher than threshold.
            points.append((int(x), int(y)) if conf > thr else None)
        if auto:

            if points[0] != None:
                isSave = True
                print('Ok!!!')
                pyautogui.moveTo(points[0][0]+640, points[0][1]+300, duration=1 / 30)
                print(points[0][0], points[0][1])
                pyautogui.click()

        for pair in POSE_PAIRS:
            partFrom = pair[0]
            partTo = pair[1]
            assert (partFrom in BODY_PARTS)
            assert (partTo in BODY_PARTS)

            idFrom = BODY_PARTS[partFrom]
            idTo = BODY_PARTS[partTo]

            if points[idFrom] and points[idTo]:
                #isSave = True
                #print('Ok!!!')
                # 移动鼠标
                #pyautogui.moveTo(points[idFrom][0], points[idFrom][1], duration=1 / 60)  # duration表示移动执行时间
                # print(points[idFrom], points[idTo])
                cv.line(frame, points[idFrom], points[idTo], (0, 255, 0), 3)
                cv.ellipse(frame, points[idFrom], (3, 3),
                           0, 0, 360, (0, 0, 255), cv.FILLED)
                cv.ellipse(frame, points[idTo], (3, 3), 0,
                           0, 360, (0, 0, 255), cv.FILLED)

        t, _ = net.getPerfProfile()
        freq = cv.getTickFrequency() / 1000

        imm = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
        video.write(imm)
        # if isSave:
        #     write_out_file("ok.jpg", frame)
        #     write_out_file(".\\output\\" + 'filename_base' + "_" + str('index') + ".jpg", frame)
        #     # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #     # plt.imshow(frame)
        #     # plt.show()
        # isSave = False
    # break
    if open('endflag.txt', 'r').read() == 'True':
        break

video.release()
os.system("rmdir output")