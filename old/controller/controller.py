import threading
import cv2
import logging
import socket
import time
import win32api
from pynput import keyboard
from pynput import mouse
import asyncio, sys
from vidgear.gears.asyncio import NetGear_Async

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

sentryIp = "192.168.1.91"
controllerIp = "192.168.1.107"
udpPort = 12345
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
        sock.sendto(b'poseT=%d\n'%poseT, (sentryIp, udpPort))
    
    if (key == keyboard.Key.alt_l):
        poseT = 0
        sock.sendto(b'poseT=%d\n'%poseT, (sentryIp, udpPort))

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
        sock.sendto(b'light=%d\n'%light, (sentryIp, udpPort))

    if (key == keyboard.Key.ctrl_l):
        safetyOff = True

    if (key == keyboard.Key.alt_l and safetyOff and poseT < 35):
        poseT += 1
        sock.sendto(b'poseT=%d\n'%poseT, (sentryIp, udpPort))


    if (key == keyboard.KeyCode.from_char('+')):
        acc += 100
        sock.sendto(b'acc=%d\n'%acc, (sentryIp, udpPort))
        print(acc)
        
    if (key == keyboard.KeyCode.from_char('-')):
        acc -= 100
        sock.sendto(b'acc=%d\n'%acc, (sentryIp, udpPort))
        print(acc)
        
    if (key == keyboard.Key.up):
        speed += 100
        sock.sendto(b'speed=%d\n'%speed, (sentryIp, udpPort))
        print(speed)
        
    if (key == keyboard.Key.down):
        speed -= 100
        sock.sendto(b'speed=%d\n'%speed, (sentryIp, udpPort))
        print(speed)
        
keyboardListener = keyboard.Listener(on_press=on_press, on_release=on_release)
keyboardListener.start()

def on_click(x, y, button, pressed):
    global captured, poseT, safetyOff

    if (not captured):
        return False

    if (button == mouse.Button.left):
        poseT = (40 if pressed and safetyOff else 0)
        sock.sendto(b'poseT=%d\n'%poseT, (sentryIp, udpPort))
        return

    if (button == mouse.Button.right and pressed):
        mouseListener.stop()
        sock.sendto(b'enable=0\n', (sentryIp, udpPort))
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
            sock.sendto(b'poseX=%d\n'%poseX, (sentryIp, udpPort))
            sock.sendto(b'poseY=%d\n'%poseY, (sentryIp, udpPort))

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

def onMouse(event, x, y, flags, param):
    global captured, mouseListener, auto

    if event == cv2.EVENT_RBUTTONDOWN:
        captured = not captured
        if captured:
            print("captured mouse")
            auto_stop()
            sock.sendto(b'enable=1\n', (sentryIp, udpPort))
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
    sock.sendto(b'acc=%d\n'%acc, (sentryIp, udpPort))
    sock.sendto(b'enable=0\n', (sentryIp, udpPort))

def auto_function(name):
    global auto, currentPoi
    while (running):
        if (auto):
            thePoi = pois[currentPoi]
            print("auto")
            print(thePoi.x)
            print(thePoi.y)
            sock.sendto(b'acc=200\n', (sentryIp, udpPort))
            sock.sendto(b'enable=1\n', (sentryIp, udpPort))
            sock.sendto(b'poseX=%d\n'%thePoi.x, (sentryIp, udpPort))
            sock.sendto(b'poseY=%d\n'%thePoi.y, (sentryIp, udpPort))
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

client=NetGear_Async(address=controllerIp, receive_mode=True, pattern=2).launch()

async def main():
    global fpsTick
    async for rawframe in client.recv_generator():
        frame = cv2.imdecode(rawframe, cv2.IMREAD_GRAYSCALE)

        if (frame is None):
            continue

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
        sock.sendto(b'rff=1\n', (sentryIp, udpPort))

        fpsTick += 1

        key=cv2.waitKey(1) & 0xFF

        #await before continuing
        await asyncio.sleep(0.00001)


if __name__ == '__main__':
    #Set event loop to client's
    asyncio.set_event_loop(client.loop)
    try:
        #run your main function task until it is complete
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        #wait for keyboard interrupt
        pass

    # close all output window
    cv2.destroyAllWindows()
    # safely close client
    client.close()
    running = False