import cv2
import threading


def cameras(VIDEO_SOURCE):
    cap0 = cv2.VideoCapture(0)
    cap1 = cv2.VideoCapture("rtsp://admin:SIBTKK@192.168.15.6:554/cam/realmonitor?channel=1&subtype=0")
    while True:
        ok, frame0 = cap0.read()
        ok, frame1 = cap1.read()
        cv2.imshow('Frame 00', frame0)
        cv2.imshow('Frame 01', frame1)
        cv2.waitKey(1)
    #return frame

def camera01():
    while True:
        frame = cameras(0)
        cv2.imshow('Frame 01', frame)

def camera02():
    while True:
        camera01 = cameras("rtsp://admin:SIBTKK@192.168.15.6:554/cam/realmonitor?channel=1&subtype=0")
        cv2.imshow('Frame 02', camera01)

cameras(0)
# threading.Thread(target=camera01).start()
# threading.Thread(target=camera02).start()