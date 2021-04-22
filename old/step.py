import RPi.GPIO as GPIO
import time

step = 17
direction = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(step, GPIO.OUT)
GPIO.setup(direction, GPIO.OUT)

GPIO.output(direction, GPIO.HIGH)
speed = 800
count = 0
while 1:
    for i in range(1, 1600):
        GPIO.output(step, GPIO.HIGH)
        time.sleep(.000001)
        GPIO.output(step, GPIO.LOW)
        if (i < speed):
            time.sleep(1 / i)
        else:
            if (i > speed):
                time.sleep(1 / (1600 - i))
        
    time.sleep(2)
    
GPIO.cleanup()
