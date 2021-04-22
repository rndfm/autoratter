# import required libraries
import socket
import threading
import serial
import cv2
from vidgear.gears.asyncio import NetGear_Async
import asyncio

UDP_IP = "0.0.0.0" # listen to everything
UDP_PORT = 12345 # port

poseX = 0
poseY = 0
poseT = 0
light = False
acc = 5000
speed = 5000

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

ser = serial.Serial('/dev/ttyUSB0', 115200)
ser.flush()

running = True
latencyTest = False
rff = True

def thread_function(name):
    global running, latencyTest, poseX, poseY, poseT, speed, acc, rff, light
    while running:
      data, _ = sock.recvfrom(512) # random buffer size, doesn't matter here..
      
      key = data.split(b'=')[0]
      value = data.split(b'=')[1]

      #simplest way to react.. of course, a better parser should be used, and add GPIO code, etc..
      if key == b'poseX':
        poseX = int(value)
        d = ('x' + str(poseX) + '\n').encode()
        ser.write(d)
      elif key== b'poseY':
        poseY = int(value)
        d = ('y' + str(poseY) + '\n').encode()
        ser.write(d)
      elif key== b'poseT':
        poseT = int(value)
        d = ('t' + str(poseT) + '\n').encode()
        ser.write(d)
      elif key== b'enable':
        enable = int(value)
        d = ('e' + str(enable) + '\n').encode()
        ser.write(d)
      elif key== b'acc':
        acc = int(value)
        d = ('a' + str(acc) + '\n').encode()
        ser.write(d)
      elif key== b'speed':
        speed = int(value)
        d = ('s' + str(speed) + '\n').encode()
        ser.write(d)
      elif key== b'rff':
        rff = True
      elif key== b'light':
        light = bool(int(value))
        d = ('l' + str(int(light)) + '\n').encode()
        ser.write(d)
        
    
controlThread = threading.Thread(target=thread_function, args=(1,))
controlThread.start()        
    

server=NetGear_Async(address='192.168.1.107', pattern=2)
#Create a async frame generator as custom source
async def my_frame_generator():
    global rff
    video = cv2.VideoCapture(0)
    video.set(cv2.CAP_PROP_CONVERT_RGB, 0) # don't process the image data
    video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
    video.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    fr = 0

    # loop over stream until its terminated
    while True:
        # read frames
        (grabbed, rawframe)=video.read()

        # check if frame empty
        if not grabbed:
            #if True break the infinite loop
            break
        
        if (rff or fr > 60):
          fr = 0
          rff = False
          # yield frame
          yield rawframe
        
        fr += 1

if __name__ == '__main__':
    #set event loop
    asyncio.set_event_loop(server.loop)
    #Add your custom source generator to Server configuration
    server.config["generator"]=my_frame_generator() 
    #Launch the Server 
    server.launch()
    try:
        #run your main function task until it is complete
        server.loop.run_until_complete(server.task)
    except KeyboardInterrupt:
        #wait for keyboard interrupt
        pass
    finally:
        # finally close the server
        server.close()
        running = False