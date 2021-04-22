import cv2
import threading

latestFrame = None
running = True
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
    print("Stopping frame grapper thread.")

def getFrame():
    return latestFrame

def stop():
    global running
    running = False

def start():
    frameGrapperThread = threading.Thread(target=frameGrapperFunction, args=(1,))
    frameGrapperThread.start()