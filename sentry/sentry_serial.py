import serial

ser = None

def start():
    global ser
    ser = serial.Serial('/dev/ttyUSB0', 115200)
    ser.flush()


def send(str):
    data = str.encode()
    ser.write(data)