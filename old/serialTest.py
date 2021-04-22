import serial
import time
import random
import keyboard
from pynput import keyboard


ser = serial.Serial('/dev/ttyUSB0',9600)
ser.flush()

acc = 5000
speed = 5000
sleep = 0.5

def on_press(key):
    global acc, speed, sleep
    print(key)
    if (key == keyboard.KeyCode.from_char('+')):
        acc += 100
        accData = ("a" + str(acc) + '\n').encode()
        ser.write(accData)
        print(accData)
        
    if (key == keyboard.KeyCode.from_char('-')):
        acc -= 100
        accData = ("a" + str(acc) + '\n').encode()
        ser.write(accData)
        print(accData)
        
    if (key == keyboard.Key.up):
        speed += 100
        accData = ("s" + str(speed) + '\n').encode()
        ser.write(accData)
        print(accData)
        
    if (key == keyboard.Key.down):
        speed -= 100
        accData = ("s" + str(speed) + '\n').encode()
        ser.write(accData)
        print(accData)
        
    if (key == keyboard.Key.left):
        sleep += 0.1
        print(sleep)
        
    if (key == keyboard.Key.right):
        sleep -= 0.1
        print(sleep)
    
    
# ...or, in a non-blocking fashion:
listener = keyboard.Listener(on_press=on_press)
listener.start()

while True:
    desPos = ("x" + str(random.randint(-1000, 1000)) + '\n').encode()
    ser.write(desPos)
    time.sleep(sleep)