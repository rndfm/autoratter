import cv2
from vidgear.gears import VideoGear
import threading
import time

video = cv2.VideoCapture(0)
# video.set(cv2.CAP_PROP_CONVERT_RGB, 0) # don't process the image data
# video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
# video.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

fpsTick = 0
fps = 0
running = True

def fpsCounter_function(name):
    global fps, fpsTick
    while (running):
        fps = fpsTick
        fpsTick = 0
        print(fps)
        time.sleep(1)

fpsCounter = threading.Thread(target=fpsCounter_function, args=(1,))
fpsCounter.start()


while True:

  try: 
    _, rawframe = video.read()

    frame = rawframe #cv2.imdecode(rawframe, cv2.IMREAD_GRAYSCALE)

    # check for frame if Nonetype
    if frame is None:
      print("No frame decoded")
      continue

    cv2.putText(frame, str(fps) + " fps", (25, 25), cv2.FONT_HERSHEY_SIMPLEX, .5,(255,255,255),2, cv2.LINE_AA)
    
    if frame.ndim == 2:
      channels = 1 #single (grayscale)

    if frame.ndim == 3:
      channels = frame.shape[-1]
    cv2.putText(frame, str(channels) + " channels", (25, 50), cv2.FONT_HERSHEY_SIMPLEX, .5,(255,255,255),2, cv2.LINE_AA)
    cv2.imshow("img", frame)
    fpsTick += 1

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

  except KeyboardInterrupt:
    break

running = False
cv2.destroyAllWindows()
video.release()
# safely close video stream
#stream.stop()