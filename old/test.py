import time
import pigpio

pi1 = pigpio.pi() 

step = 17
direction = 27


pi1.set_mode(step, pigpio.OUTPUT) # GPIO 17 as output
pi1.set_mode(direction, pigpio.OUTPUT) # GPIO 27 as output


pi1.write(direction, 0)

pi1.set_PWM_frequency(step, 500)
pi1.set_PWM_dutycycle(step, 64) # PWM 1/4 on

while 1:
    
    time.sleep(1)
    
pi1.stop()

