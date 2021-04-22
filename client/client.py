import socket
import cv2
import pickle
import struct
import threading
import time

#import logging
import win32api
from pynput import keyboard
from pynput import mouse

sentryHost = "95.209.144.32"
sentryPortVideo = 5000
sentryPortControls = 5001

running = True
captured = False
poseX = 0
poseY = 0
poseT = 0
safetyOff = False
poseXMax = 5000
poseYMax = 2000
screenCenterX = 0
screenCenterY = 0
fpsTick = 0
fps = 0
mouseListener = None
acc = 5000
speed = 5000
font = cv2.FONT_HERSHEY_DUPLEX
pois = []
auto = False
currentPoi = 0
light = False

class poi:
    def __init__(self, x, y):
        self.x=x
        self.y=y

def on_release(key):
    global safetyOff, poseT
    if not captured:
        return

    if (key == keyboard.Key.ctrl_l):
        safetyOff = False
        poseT = 0
        sock.sendto(b'poseT=%d\n'%poseT, (sentryHost, sentryPortControls))
    
    if (key == keyboard.Key.alt_l):
        poseT = 0
        sock.sendto(b'poseT=%d\n'%poseT, (sentryHost, sentryPortControls))

def on_press(key):
    global acc, speed, captured, running, safetyOff, poseT, auto, pois, light

    if not captured:
        if (key == keyboard.KeyCode.from_char('a')):
            auto = not auto
            if (not auto):
                auto_stop()
        return

    if (key == keyboard.KeyCode.from_char('q')):
        running = False
        return False
    
    if (key == keyboard.KeyCode.from_char('p')):
        newPoi = poi(poseX, poseY)
        pois.append(newPoi)
        print("point added")
        print(newPoi.x)
        print(newPoi.y)
    
    if (key == keyboard.KeyCode.from_char('l')):
        light = not light
        sock.sendto(b'light=%d\n'%light, (sentryHost, sentryPortControls))

    if (key == keyboard.Key.ctrl_l):
        safetyOff = True

    if (key == keyboard.Key.alt_l and safetyOff and poseT < 35):
        poseT += 1
        sock.sendto(b'poseT=%d\n'%poseT, (sentryHost, sentryPortControls))


    if (key == keyboard.KeyCode.from_char('+')):
        acc += 100
        sock.sendto(b'acc=%d\n'%acc, (sentryHost, sentryPortControls))
        print(acc)
        
    if (key == keyboard.KeyCode.from_char('-')):
        acc -= 100
        sock.sendto(b'acc=%d\n'%acc, (sentryHost, sentryPortControls))
        print(acc)
        
    if (key == keyboard.Key.up):
        speed += 100
        sock.sendto(b'speed=%d\n'%speed, (sentryHost, sentryPortControls))
        print(speed)
        
    if (key == keyboard.Key.down):
        speed -= 100
        sock.sendto(b'speed=%d\n'%speed, (sentryHost, sentryPortControls))
        print(speed)
        
keyboardListener = keyboard.Listener(on_press=on_press, on_release=on_release)
keyboardListener.start()

def on_click(x, y, button, pressed):
    global captured, poseT, safetyOff

    if (not captured):
        return False

    if (button == mouse.Button.left):
        poseT = (40 if pressed and safetyOff else 0)
        sock.sendto(b'poseT=%d\n'%poseT, (sentryHost, sentryPortControls))
        return

    if (button == mouse.Button.right and pressed):
        mouseListener.stop()
        sock.sendto(b'enable=0\n', (sentryHost, sentryPortControls))
        print("mouse released")
        return False

def on_move(x, y):
    global captured, poseX, poseY
    
    if (captured):
        if (x != screenCenterX or y != screenCenterY):
            # read offset from center
            offsetX = x - screenCenterX
            offsetY = y - screenCenterY

            # reset mouse cursor to center
            mouse.Controller().position = (screenCenterX, screenCenterY)

            # add offset to pose
            poseX = poseX + offsetX
            poseY = poseY + offsetY

            # cap pose to prevent runaway
            if (poseX > poseXMax):
                poseX = poseXMax

            if (poseX < -poseXMax):
                poseX = -poseXMax

            if (poseY > poseYMax):
                poseY = poseYMax

            if (poseY < -poseYMax):
                poseY = -poseYMax

            # send updated pose over network
            sock.sendto(b'poseX=%d\n'%poseX, (sentryHost, sentryPortControls))
            sock.sendto(b'poseY=%d\n'%poseY, (sentryHost, sentryPortControls))

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

def onMouse(event, x, y, flags, param):
    global captured, mouseListener, auto

    if event == cv2.EVENT_RBUTTONDOWN:
        captured = not captured
        if captured:
            print("captured mouse")
            auto_stop()
            sock.sendto(b'enable=1\n', (sentryHost, sentryPortControls))
            win32api.SetCursorPos((screenCenterX, screenCenterY))
            mouseListener = mouse.Listener(on_move=on_move, on_click=on_click, suppress=True)
            mouseListener.start()

def fpsCounter_function(name):
    global fps, fpsTick
    while (running):
        fps = fpsTick
        fpsTick = 0
        time.sleep(1)

fpsCounter = threading.Thread(target=fpsCounter_function, args=(1,))
fpsCounter.start()

def auto_stop():
    global auto
    auto = False
    sock.sendto(b'acc=%d\n'%acc, (sentryHost, sentryPortControls))
    sock.sendto(b'enable=0\n', (sentryHost, sentryPortControls))

def auto_function(name):
    global auto, currentPoi
    while (running):
        if (auto):
            thePoi = pois[currentPoi]
            print("auto")
            print(thePoi.x)
            print(thePoi.y)
            sock.sendto(b'acc=200\n', (sentryHost, sentryPortControls))
            sock.sendto(b'enable=1\n', (sentryHost, sentryPortControls))
            sock.sendto(b'poseX=%d\n'%thePoi.x, (sentryHost, sentryPortControls))
            sock.sendto(b'poseY=%d\n'%thePoi.y, (sentryHost, sentryPortControls))
            currentPoi += 1
            if (currentPoi >= len(pois)):
                currentPoi = 0
        time.sleep(8)

autoThread = threading.Thread(target=auto_function, args=(1,))
autoThread.start()

cv2.namedWindow('Output Frame', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Output Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
screenWidth = win32api.GetSystemMetrics(0)
screenHeight = win32api.GetSystemMetrics(1)
print(screenWidth)
print(screenHeight)
screenCenterX = int(screenWidth / 2)
screenCenterY = int(screenHeight / 2)

cv2.setMouseCallback('Output Frame', onMouse)

def main():
    global fpsTick
    sock = socket.socket()
    data = bytearray()
    payload_size = struct.calcsize("I")

    try:
        sock.connect((sentryHost, sentryPortVideo))
        sock.send(b'r')
        while True:
            try:
                while len(data) < payload_size:
                    data.extend(sock.recv(4096))
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("I", packed_msg_size)[0]
                while len(data) < msg_size:
                    data.extend(sock.recv(4096))
                frame_data = data[:msg_size]
                data = data[msg_size:]
                if frame_data=='':
                    break
                rawframe=pickle.loads(frame_data)

                frame = cv2.imdecode(rawframe, cv2.IMREAD_GRAYSCALE)
                cv2.putText(frame, str(fps) + " fps", (10, 20), font, .5,(255,255,255), 1, cv2.LINE_AA)
                cv2.putText(frame, str(acc) + " acc", (10, 40), font, .5,(255,255,255), 1, cv2.LINE_AA)
                cv2.putText(frame, str(speed) + " spd", (10, 60), font, .5,(255,255,255), 1, cv2.LINE_AA)
                cv2.putText(frame, "x:" + str(poseX) + " y:" + str(poseY), (10, 80), font, .5,(255,255,255), 1, cv2.LINE_AA)

                if (light):
                    cv2.putText(frame, "light", (10, 100), font, .5,(255,255,255), 1, cv2.LINE_AA)

                if (safetyOff):
                    height, width = frame.shape
                    cv2.rectangle(frame, (0, 0), (width - 2, height - 2), 255, 2)
                    cv2.putText(frame, "safety off", (10, 120), font, .5,(255,255,255), 1, cv2.LINE_AA)
                    cv2.putText(frame, "Tigger pos: " + str(poseT), (10, 140), font, .5,(255,255,255), 1, cv2.LINE_AA)

                if (auto):
                    cv2.putText(frame, "AUTO", (10, 120), font, .5,(255,255,255), 1, cv2.LINE_AA)

                cv2.imshow("Output Frame", frame)
                cv2.waitKey(1)
                sock.send(b'r')
                fpsTick += 1
            except (KeyboardInterrupt, SystemExit):
                print("Exiting...")
                break
            except socket.error as e:
                print(str(e))
                break
    except socket.error as e:
        print(str(e))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        #wait for keyboard interrupt
        pass

    sock.close()
    running = False
    cv2.destroyAllWindows()