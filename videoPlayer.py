from threading import Thread, Semaphore, Lock
import cv2, time, sys, os
import numpy as np

fileName = 'clip.mp4'
semaphore = Semaphore(10)
lock = Lock()
extractQueue = []
grayscaleQueue = []

class extractFrames(Thread):
    def __init__(self, fileName):
        Thread.__init__(self)
        self.fileName = fileName
        self.count = 0
    def run(self):
        count = 0
        vidcap = cv2.VideoCapture(self.fileName)
        frameCount = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        success, frame = vidcap.read()

        while True:
            if (success and len(extractQueue) <= 10):
                semaphore.acquire()
                lock.acquire()
                extractQueue.append(frame)
                lock.release()
                semaphore.release()

                success, frame = vidcap.read()
                print("Reading frames: ", self.count)
                self.count += 1

            if(self.count >= frameCount):
                semaphore.acquire()
                lock.acquire()
                extractQueue.append(-1)
                lock.release()
                semaphore.release()
                break
        return
class convertToGrayscale(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.count = 0
    def run(self):

        while True:
            if((len(extractQueue) > 0) and len(grayscaleQueue) < 10):
                semaphore.acquire()
                lock.acquire()
                frame  = extractQueue.pop(0)
                lock.release()
                semaphore.release()

                if((type(frame) == int) and (frame == -1)):
                    semaphore.acquire()
                    lock.acquire()
                    grayscaleQueue.append(-1)
                    lock.release()
                    semaphore.release()
                    break
                print("Converting Frame:", self.count)
                grayscaleFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                semaphore.acquire()
                lock.acquire()
                grayscaleQueue.append(grayscaleFrame)
                lock.release
                semaphore.release()

                self.count += 1
        return
class displayFrames(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.delay = 42
        self.count = 0
    def run(self):

        while True:
            if(len(grayscaleQueue) > 0):
                semaphore.acquire()
                lock.acquire()
                frame = grayscaleQueue.pop(0)
                lock.release()
                semaphore.release()

                if((type(frame) ==int) and (frame == -1)):
                    break

                cv2.imshow('Video', frame)

                if(cv2.waitKey(self.delay) and 0xFF == ord("q")):
                   break
        cv2.destroyAllWindows()
        return
    
extract = extractFrames(fileName)
extract.start()
convert = convertToGrayscale()
convert.start()
display = displayFrames()
display.start()
   
