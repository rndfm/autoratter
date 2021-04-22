
import threading
import cv2
import pickle
import struct

UDP_IP = "0.0.0.0" # listen to everything
UDP_PORT = 12345 # port

poseX = 0
poseY = 0
poseT = 0
light = False
acc = 5000
speed = 5000

running = True
latestFrame = None

def frameGrapperFunction(name):
  global latestFrame
  video = cv2.VideoCapture(0)
  video.set(cv2.CAP_PROP_CONVERT_RGB, 0) # don't process the image data
  video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
  video.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
  video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

  while running:
    (grabbed, latestFrame)=video.read()
    if not grabbed:
      #if True break the infinite loop
      print("Frame grap failed.")
      break

    #_, latestFrame = cv2.imencode('.jpg', newFrame)
    #frame = cv2.imdecode(latestFrame, cv2.IMREAD_GRAYSCALE)
    # cv2.imshow("test", latestFrame)
    # cv2.waitKey(1)
    # check if frame empty



def clientVideoThread(clientsocket,addr):
  print("starting video streaming...")
  while True:
    try:
      _ = clientsocket.recv(1) # Wait for "ready for next frame" from client.
      
      frame = pickle.dumps(latestFrame)
      size = len(frame)
      p = struct.pack('I', size)
      frame = p + frame
      clientsocket.sendall(frame)
    except socket.error as e:
      print("client disconnected", addr)
      break

  clientsocket.close()


if __name__ == '__main__':
    try:
        # controlThread = threading.Thread(target=thread_function, args=(1,))
        # controlThread.start()

        frameGrapperThread = threading.Thread(target=frameGrapperFunction, args=(1,))
        frameGrapperThread.start()
        
        s = socket.socket()         # Create a socket object
        host = "0.0.0.0" # Get local machine name
        print(host)
        port = 50000                # Reserve a port for your service.

        print('Server started!')
        print('Waiting for clients...')

        s.bind((host, port))        # Bind to the port
        s.listen(5)                 # Now wait for client connection.

        while True:
          c, addr = s.accept()     # Establish connection with client.
          print('Got connection from', addr)
          threading.Thread(target=clientVideoThread, args=(c,addr)).start()

        s.close()
    except KeyboardInterrupt:
        #wait for keyboard interrupt
        pass
    finally:
        running = False