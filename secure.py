import os
import RPi.GPIO as go
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import requests
import time
import sys
import signal
import ast
import base64
import shlex
import subprocess
import random

def rear(t):
    go.output(7, False)
    go.output(11,True)
    go.output(13,False)
    go.output(15,True)
    time.sleep(t)
    go.output(7, False)
    go.output(11,False)
    go.output(13,False)
    go.output(15,False)

def front(t):
    go.output(7, True)
    go.output(11,False)
    go.output(13,True)
    go.output(15,False)
    time.sleep(t)
    go.output(7, False)
    go.output(11,False)
    go.output(13,False)
    go.output(15,False)

def right(t):
    go.output(7, True)
    go.output(11,False)
    go.output(13,False)
    go.output(15,True)
    time.sleep(t)
    go.output(7, False)
    go.output(11,False)
    go.output(13,False)
    go.output(15,False)

def left(t):
    go.output(7, False)
    go.output(11,True)
    go.output(13,True)
    go.output(15,False)
    time.sleep(t)
    go.output(7, False)
    go.output(11,False)
    go.output(13,False)
    go.output(15,False)

def stop():
    go.output(7, False)
    go.output(11,False)
    go.output(13,False)
    go.output(15,False)

def beep():
    go.output(38, True)
    go.output(40, False)
    time.sleep(1)
    go.output(38, False)
    go.output(40, False)

def attack():
    go.output(37, True)
    go.output(38, True)
    go.output(40, False)
    time.sleep(0.5)
    go.output(37, False)
    go.output(38, False)
    go.output(40, False)

def measure():
    go.output(trigger_pin, go.HIGH)
    time.sleep(0.00001)
    go.output(trigger_pin, go.LOW)
    while go.input(echo_pin) == go.LOW:
        pulse_start = time.time()
    while go.input(echo_pin) == go.HIGH:
        pulse_end   = time.time()
    t = pulse_end - pulse_start
    d = (t * v) / 2
    return d * 100

def secure():

    global interrupt
    try:
        pid = os.fork()
        if pid == 0: # child process
            count = 0
            camera = PiCamera()
            camera.resolution = (320, 240)
            camera.framerate = 32
            rawCapture = PiRGBArray(camera, size=(320,240))
            time.sleep(2)
            print("start detecting faces!")
            for frame in camera.capture_continuous(rawCapture,format="bgr",use_video_port=True):
                flag = 1
                image = frame.array
                face = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
                #hog = cv2.HOGDescriptor()
                #hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                #(rect2, weights) = hog.detectMultiScale(gray, winStride=(4, 4), padding=(8,8), scale=1.05)
                face_pos = face.detectMultiScale(gray, 1.1, 5)
                for (x,y,w,h) in face_pos:
                    cv2.rectangle(image,(x,y),(x+w,y+h),(255,2,2),2)
                    count = count + 1
                    flag = 0
                if count == 1:
                    # send server picture first
                    # active beep for 5 seconds
                    beep()
                    cv2.imwrite('img.jpg',image)
                    with open('img.jpg','rb') as f:
                        img = base64.b64encode(f.read())
                        r = requests.post('http://140.113.89.234:8888', data={'img_exist': '1','img': img})
                        print(img)
                    count = 0
                if flag:
                    count = 0
                cv2.waitKey(1) & 0xFF
                rawCapture.truncate(0)
                cv2.imshow('result',image)

        else:
            while True:
                f2 = open('int.txt', 'r')
                temp2 = f2.read(1)
                f2.close()
                if measure() < 20:
                    #turn = random.randint(0,1)
                    turn = 1
                    if turn == 0:
                        left(0.5)
                    else:
                        right(0.5)
                else:
                    front(0.5)
                if temp2=='1':
                    os.kill(pid, signal.SIGKILL)
                    break
    except OSError:
        print ("secure fork error")
    go.cleanup()
    sys.exit(0)


def killing():
    while True:
        fkill = open('kill.txt', 'r')
        temp = fkill.read(1)
        fkill.close()
        if temp == '1':
            go.cleanup()
            sys.exit(0)
        elif temp == 'w':
            print('fuck')
            front(0.5)
        elif temp == 'a':
            left(0.5)
        elif temp == 'd':
            right(0.5)
        elif temp == 's':
            rear(0.5)
        elif temp == 'x':
            stop()
        elif temp == 'k':
            attack()

        else:
            stop()


if __name__ == "__main__":
    # mode1: secure
    # mode2: killing
    v = 343  # 331 + 0.6 * 20
    trigger_pin = 16
    echo_pin    = 18
    global pro


    mode = 'secure'
    while True:
        go.setmode(go.BOARD)
        # for distance detector
        go.setup(trigger_pin, go.OUT)
        go.setup(echo_pin, go.IN)
        # for car's movement
        go.setup(7,  go.OUT)
        go.setup(11, go.OUT)
        go.setup(13, go.OUT)
        go.setup(15, go.OUT)
        go.setup(37, go.OUT)
        go.setup(38, go.OUT)
        go.setup(40, go.OUT)
        time.sleep(2)
        interrupt = 0

        file = open('int.txt', 'w')
        file.write('0')
        file.close()

        fkill= open('kill.txt', 'w')
        fkill.write('x')
        fkill.close()
        try:
            ppid = os.fork()
            if ppid == 0: # child process
                # receive mode
                if mode == 'secure':
                    secure()
                elif mode == 'killing':
                    killing()
            else: # parent process
                while True:
                    rr = requests.get('http://140.113.89.234:8888')
                    r = ast.literal_eval(rr.text)
                    if mode == 'secure':
                        if r['mode'] == 'mode2':
                            file = open('int.txt', 'w')
                            file.write('1')
                            file.close()
                            cmd = 'sudo python3 ./pistreaming/server.py'
                            args = shlex.split(cmd)
                            #pro = subprocess.Popen(cmd,shell=True)
                            pro = subprocess.Popen(args)
                            mode = 'killing'
                            status1 = os.waitpid(ppid, 0)
                            break
                    elif mode == 'killing':
                        if r['mode'] == 'mode2':
                            #print(r["dir"])
                            fkill = open('kill.txt', 'w')
                            if r['dir'] == 'w':
                                print('Mark ')
                                fkill.write('w')
                            elif r['dir'] == 'a':
                                fkill.write('a')
                            elif r['dir'] == 's':
                                fkill.write('s')
                            elif r['dir'] == 'd':
                                fkill.write('d')
                            elif r['dir'] == 'x':
                                fkill.write('x')
                            elif r['dir'] == 'k':
                                fkill.write('k')
                            else:
                                fkill.write('x')
                            fkill.close()
                        elif r['mode'] == 'mode1':
                            fkill = open('kill.txt', 'w')
                            fkill.write('1')
                            fkill.close()
                            print(os.kill((pro.pid), signal.SIGINT))
                            mode = 'secure'
                            status2 = os.waitpid(ppid, 0)
                            time.sleep(5)
                            break

        except OSError:
            print ("main fork error")
