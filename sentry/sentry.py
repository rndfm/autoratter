import socket
import threading
import time
import sentry_serial as serial
import sentry_video as video
import sentry_server as server

server.setFrameProvider(video.getFrame)

poseX = 0
poseY = 0
poseT = 0
light = False
acc = 5000
speed = 5000
running = True

serial.start()
video.start()
server.start()

def thread_function(name):
    global running, poseX, poseY, poseT, speed, acc, light

    UDP_IP = "0.0.0.0" # listen to everything
    UDP_PORT = 5001 # port
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while running:
      data, _ = sock.recvfrom(512) # random buffer size, doesn't matter here..
      
      key = data.split(b'=')[0]
      value = data.split(b'=')[1]

      #simplest way to react.. of course, a better parser should be used, and add GPIO code, etc..
      if key == b'poseX':
        poseX = int(value)
        serial.send('x' + str(poseX) + '\n')
      elif key== b'poseY':
        poseY = int(value)
        serial.send('y' + str(poseY) + '\n')
      elif key== b'poseT':
        poseT = int(value)
        serial.send('t' + str(poseT) + '\n')
      elif key== b'enable':
        enable = int(value)
        serial.send('e' + str(enable) + '\n')
      elif key== b'acc':
        acc = int(value)
        serial.send('a' + str(acc) + '\n')
      elif key== b'speed':
        speed = int(value)
        serial.send('s' + str(speed) + '\n')
      elif key== b'light':
        light = bool(int(value))
        serial.send('l' + str(int(light)) + '\n')
        
    
controlThread = threading.Thread(target=thread_function, args=(1,))
controlThread.start()        
    

if __name__ == '__main__':
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        #wait for keyboard interrupt
        print("Exiting...")
        pass
    finally:
        video.stop()
        server.stop()
        running = False