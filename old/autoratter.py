# import required libraries
from vidgear.gears import VideoGear
from vidgear.gears import NetGear
import socket
import threading
import serial
import cv2

UDP_IP = "0.0.0.0" # listen to everything
UDP_PORT = 12345 # port

poseX = 0
poseY = 0

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

ser = serial.Serial('/dev/ttyUSB1',9600)
ser.flush()

running = True
latencyTest = False

def thread_function(name):
    global running, latencyTest, poseX, poseY
    while running:
      data, addr = sock.recvfrom(512) # random buffer size, doesn't matter here..
      
      key = data.split(b'=')[0]
      value = data.split(b'=')[1]

      #simplest way to react.. of course, a better parser should be used, and add GPIO code, etc..
      if key == b'poseX':
        poseX = int(value)
      elif key== b'poseY':
        poseY = int(value)
      elif key== b'latencyTest':
        latencyTest = True
        print('latency test received...')
        continue
    
      d = (str(poseX) + '\n').encode()
      ser.write(d)

        
controlThread = threading.Thread(target=thread_function, args=(1,))
controlThread.start()        
    

# open any valid video stream(for e.g `test.mp4` file)
options = {"CAP_PROP_FRAME_WIDTH ":320, "CAP_PROP_FRAME_HEIGHT":240, "CAP_PROP_FPS ":60}

stream = VideoGear(source=0, **options).start()

#Define Netgear Server with default parameters
server = NetGear(address='69.69.69.1') 

# loop over until KeyBoard Interrupted
while True:

  try: 

     # read frames from stream
    frame = stream.read()

    # check for frame if Nonetype
    if frame is None:
        break
    
    if latencyTest:
        cv2.rectangle(frame,(0,0),(10,10),(0,255,0),-1)
        latencyTest = False
    
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # send frame to server
    server.send(frame)

  except KeyboardInterrupt:
    break

running = False
# safely close video stream
stream.stop()

# safely close server
server.close()