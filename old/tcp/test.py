import cv2
video = cv2.VideoCapture(0)
# video.set(cv2.CAP_PROP_CONVERT_RGB, 1) # don't process the image data
# video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
# video.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
  (grabbed, frame)=video.read()
  if not grabbed:
    #if True break the infinite loop
    print("Frame grap failed.")
    break

  #frame = cv2.imdecode(latestFrame, cv2.IMREAD_GRAYSCALE)
  cv2.imshow("test", frame)