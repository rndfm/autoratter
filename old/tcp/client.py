import socket
import cv2
import pickle
import struct
import threading
import time

sock = socket.socket()
host = '192.168.1.91'
port = 5000

data = bytearray()
payload_size = struct.calcsize("I")
fps = 0
fpsTick = 0
font = cv2.FONT_HERSHEY_DUPLEX
running = True

def fpsCounter_function(name):
    global fps, fpsTick, running
    while running:
        fps = fpsTick
        fpsTick = 0
        time.sleep(1)

fpsCounter = threading.Thread(target=fpsCounter_function, args=(1,))
fpsCounter.start()

try:
    sock.connect((host, port))
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
            cv2.imshow("test2", frame)
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

sock.close()
running = False
cv2.destroyAllWindows()
