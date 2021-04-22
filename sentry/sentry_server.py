import socket
import threading
import pickle
import struct
import ctypes
import time

getFrame = None
serverThread = None
clientThreads = []
port = 5000
host = "0.0.0.0"

def setFrameProvider(provider):
    global getFrame
    getFrame = provider

def clientVideoThread(clientsocket,addr):
    print("starting video streaming...")
    clientsocket.settimeout(5)
    frames = 0
    while True:
        try:
            frames += 1
            if (frames > 10):
                frames = 0
                _ = clientsocket.recv(1) # Wait for "ready for next frame" from client.
            
            frame = pickle.dumps(getFrame())
            size = len(frame)
            p = struct.pack('I', size)
            frame = p + frame
            clientsocket.sendall(frame)
        except (KeyboardInterrupt, SystemExit):
            print("Client thread exited.")
            break
        except socket.error:
            print("client disconnected", addr)
            break

def serverThreadFunction():
    serverSocket = socket.socket()         # Create a socket object
    serverSocket.bind((host, port))        # Bind to the port
    serverSocket.listen(5)                 # Now wait for client connection.
    serverSocket.settimeout(5)
    print('Server started!')
    print('Waiting for clients...')
    while True:
        try:
            c, addr = serverSocket.accept()     # Establish connection with client.
            print('Got connection from', addr)
            clientThread = threading.Thread(target=clientVideoThread, args=(c,addr))
            clientThreads.append(clientThread)
            clientThread.start()
        except (KeyboardInterrupt, SystemExit):
            print("Server thread exited.")
            break
        except socket.timeout:
            pass

    print("Server thread exited.")

def start():
    global serverThread
    serverThread = threading.Thread(target=serverThreadFunction)
    serverThread.start()

def stop():
    if (serverThread.is_alive()):
        print("Stopping server thread:", serverThread.ident)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(serverThread.ident, ctypes.py_object(SystemExit))
        if res > 1: 
            print('Exception raise failure') 

    
    for thread in clientThreads:
        if (thread.is_alive()):
            print("Stopping client thread:", thread.ident)
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, ctypes.py_object(SystemExit)) 