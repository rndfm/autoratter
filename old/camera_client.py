# import required libraries
from vidgear.gears import NetGear
import threading
import cv2
import logging
import socket
import time
import win32api
from pynput import keyboard
from pynput import mouse

UDP_IP = "69.69.69.2" # set it to destination IP.. RPi in this case
UDP_PORT = 12345
running = True
captured = False
poseX = 0
poseY = 0
poseXMax = 1000
poseYMax = 800
screenCenterX = 0
screenCenterY = 0
fpsTick = 0
fps = 0
latencyTestStartTime = time.time()
latencyTestRunning = False
latencyResult = 0
mouseListener = None
acc = 5000
speed = 5000

def on_press(key):
    global acc, speed, captured
    if not captured:
        return

    if (key == keyboard.KeyCode.from_char('q')):
        running = False
        return False

    if (key == keyboard.KeyCode.from_char('+')):
        acc += 100
        sock.sendto(b'acc=%d\n'%acc, (UDP_IP, UDP_PORT))
        print(acc)
        
    if (key == keyboard.KeyCode.from_char('-')):
        acc -= 100
        sock.sendto(b'acc=%d\n'%acc, (UDP_IP, UDP_PORT))
        print(acc)
        
    if (key == keyboard.Key.up):
        speed += 100
        sock.sendto(b'speed=%d\n'%speed, (UDP_IP, UDP_PORT))
        print(speed)
        
    if (key == keyboard.Key.down):
        speed -= 100
        sock.sendto(b'speed=%d\n'%speed, (UDP_IP, UDP_PORT))
        print(speed)
        
# ...or, in a non-blocking fashion:
keyboardListener = keyboard.Listener(on_press=on_press)
keyboardListener.start()

def on_click(x, y, button, pressed):
    global captured
    if (not pressed):
        return
    
    if (not captured):
        return False

    if (button == mouse.Button.right):
        mouseListener.stop()
        print("mouse released")
        return False

def on_move(x, y):
    global captured, centerCalibration, poseX, poseY
    
    if (captured):
        if (x != screenCenterX or y != screenCenterY):
            # read offset from center
            offsetX = x - screenCenterX
            offsetY = y - screenCenterY

            # reset mouse cursor to center
            mouse.Controller().position = (screenCenterX, screenCenterY)
            #mouse.position = (screenCenterX, screenCenterY)
            #win32api.SetCursorPos((screenCenterX, screenCenterY))

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

            print('poseX = %d, poseY = %d'%(poseX, poseY))

            # send updated pose over network
            sock.sendto(b'poseX=%d\n'%poseX, (UDP_IP, UDP_PORT))
            sock.sendto(b'poseY=%d\n'%poseY, (UDP_IP, UDP_PORT))

print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

def onMouse(event, x, y, flags, param):
    global captured, mouseListener

    if event == cv2.EVENT_RBUTTONDOWN:
        captured = not captured
        if captured:
            print("captured mouse")
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

def latencyTest_function(name):
    global latencyTestRunning, latencyTestStartTime
    while (running):
        latencyTestRunning = True
        latencyTestStartTime = time.time()
        sock.sendto(b'latencyTest=True\n', (UDP_IP, UDP_PORT))
        time.sleep(1)

latencyTest = threading.Thread(target=latencyTest_function, args=(1,))
latencyTest.start()

cv2.namedWindow('Output Frame', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Output Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
#cv2.resizeWindow('Output Frame', 600,600)
screenWidth = win32api.GetSystemMetrics(0)
screenHeight = win32api.GetSystemMetrics(1)
screenCenterX = int(screenWidth / 2)
screenCenterY = int(screenHeight / 2)

#cv2.moveWindow('Output Frame', int(screenCenterX - frameCenterX), int(screenCenterY - frameCenterY))

cv2.setMouseCallback('Output Frame', onMouse)

# define Netgear Client with `receive_mode = True` and default parameter
client = NetGear(receive_mode = True)

# loop over
while running:

    # receive frames from network
    frame = client.recv()

    # check for received frame if Nonetype
    if frame is None:
        break


    # Test for visual latency indicator feedback
    if latencyTestRunning:
        b,g,r = (frame[5, 5])
        if(b<10 and g>250 and r<10):
            latencyResult = int((time.time() - latencyTestStartTime) * 1000)
            latencyTestRunning = False


    # Show output window
    cv2.putText(frame, str(latencyResult) + " ms", (25, 20), cv2.FONT_HERSHEY_SIMPLEX, .5,(255,255,255),2, cv2.LINE_AA)
    cv2.putText(frame, str(fps) + " fps", (25, 40), cv2.FONT_HERSHEY_SIMPLEX, .5,(255,255,255),2, cv2.LINE_AA)
    cv2.putText(frame, str(acc) + " acc", (25, 60), cv2.FONT_HERSHEY_SIMPLEX, .5,(255,255,255),2, cv2.LINE_AA)
    cv2.putText(frame, str(speed) + " spd", (25, 80), cv2.FONT_HERSHEY_SIMPLEX, .5,(255,255,255),2, cv2.LINE_AA)
    cv2.imshow("Output Frame", frame)
    
    fpsTick += 1

    # check for 'q' key if pressed
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break


running = False

# close output window
cv2.destroyAllWindows()

# safely close client
client.close()