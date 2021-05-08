from Interpolate import Interpolate
from cv2 import cv2

font = cv2.FONT_HERSHEY_DUPLEX

class Scope:
    scopeFrameOffset = (0, 0)
    scopeFrameAdjust = False
    rangeAdjustment = False

    rangeOffsets = []
    rangeOffsetCurrent = 0
    rangeMeters = 10
    interpolator = None

    def loadRangeOffsets(self):
        with open("rangeOffsets.txt", "r") as rangeOffsetsFile:
            lines = rangeOffsetsFile.readlines()
            
            for l in lines:
                values = l.split(",")
                self.rangeOffsets.append((int(values[0]), float(values[1])))
            
        self.updateIntepolator()

    def saveRangeOffsets(self):
        with open("rangeOffsets.txt", "w") as rangeOffsetsFile:
            for offset in self.rangeOffsets:
                rangeOffsetsFile.write(str(offset[0]) + "," + str(offset[1]) +"\n")

    def __init__(self):
        print("scope init")
        self.loadRangeOffsets()
        self.loadFrameOffset()
        
    def loadFrameOffset(self):
        with open("frameOffset.txt", "r") as frameOffsetFile:
            lines = frameOffsetFile.readlines()
            values = lines[0].split(",")
            scopeY = int(values[0])
            scopeX = int(values[1])
            self.scopeFrameOffset = (scopeY, scopeX)

    def setFrameOffset(self, offset):
        self.scopeFrameOffset = offset
        with open('frameOffset.txt', 'w') as fp:
            fp.write(str(self.scopeFrameOffset[0]) + "," + str(self.scopeFrameOffset[1]))

      
    def getOffsetAtRange(self, range):
        if self.interpolator is not None:
            return self.interpolator(range)
        
    def updateIntepolator(self):
        xlist, ylist = zip(*self.rangeOffsets)
        self.interpolator = Interpolate(xlist, ylist)
        self.rangeOffsetCurrent = self.getOffsetAtRange(self.rangeMeters)

    def setOffsetAtRange(self, rangeMeters, offset):
        index = -1
        for i, v in enumerate(self.rangeOffsets):
            if v[0] == rangeMeters:
                index = i
                break
        if index >= 0:
            self.rangeOffsets[index] = (int(rangeMeters), float(offset))
        else:
            self.rangeOffsets.append((int(rangeMeters), float(offset)))

        self.rangeOffsets.sort(key=lambda x: x[0])
        print(self.rangeOffsets)
        self.updateIntepolator()
        self.saveRangeOffsets()
        

    def setRange(self, range):
        self.rangeMeters = range
        self.rangeOffsetCurrent = self.getOffsetAtRange(self.rangeMeters)

    def draw(self, frame):
        if (self.scopeFrameAdjust):
            self.drawAdjustmentLines(frame)
            return

        frameHeight, frameWidth = frame.shape[:2]
        frameCenterY = int(frameHeight/2)
        frameCenterX = int(frameWidth/2)
        scopeY, scopeX = self.scopeFrameOffset

        color = (0, 255, 0)
        if (self.rangeAdjustment):
            color = (255, 0, 0)
        
        cv2.circle(frame, (frameCenterX + scopeX, frameCenterY + scopeY - int(self.rangeOffsetCurrent)), 2, color, -1)
        cv2.putText(frame, "r:" + str(self.rangeMeters) + "m", (frameCenterX + scopeX + 200, frameCenterY + scopeY), font, .5, color, 1, cv2.LINE_AA)

    def drawAdjustmentLines(self, frame):
        frameHeight, frameWidth = frame.shape[:2]
        frameCenterY = int(frameHeight/2)
        frameCenterX = int(frameWidth/2)
        scopeY, scopeX = self.scopeFrameOffset

        cv2.line(frame, (0, frameCenterY + scopeY),(frameWidth, frameCenterY + scopeY), (0, 255, 0), 1)
        cv2.line(frame, (frameCenterX + scopeX, 0),(frameCenterX + scopeX, frameHeight), (0, 255, 0), 1)

    def __call__(self, frame):
        frameHeight, frameWidth = frameBgr.shape[:2]
        frameCenterY = int(frameHeight/2)
        frameCenterX = int(frameWidth/2)

        cv2.line(frame, (0, frameCenterY + scopeY),(frameWidth, frameCenterY + scopeY), (0, 255, 0), 1)
        cv2.line(frame, (frameCenterX + scopeX, 0),(frameCenterX + scopeX, frameHeight), (0, 255, 0), 1)