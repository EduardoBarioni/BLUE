import cv2
import numpy as np
import sys

TEXT_COLOR = (0,255,0)
TRACKER_COLOR = (255,0,0)
FONT = cv2.FONT_HERSHEY_SIMPLEX
#VIDEO_SOURCE = "test_videos/solidWhiteRight.mp4"
#VIDEO_SOURCE = "project_video.mp4"
#VIDEO_SOURCE = "http://192.168.55.116:4747/video"
#VIDEO_SOURCE = "rtsp://admin:SIBTKK@192.168.55.116/cam/realmonitor?channel=1&subtype=0" #REDE AGVS
#VIDEO_SOURCE = "rtsp://admin:SIBTKK@192.168.0.109/cam/realmonitor?channel=1&subtype=0" #REDE AGVS_escritório
VIDEO_SOURCE = "/home/user/AGVS repository/OpenCV/04.mp4"
#VIDEO_SOURCE = 0


BGS_TYPES = ["GMG", "MOG", "MOG2", "KNN", "CNT"]
BGS_TYPE = BGS_TYPES[2]

def getKernel(KERNEL_TYPE):
    if KERNEL_TYPE == 'dilation':
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    if KERNEL_TYPE == 'opening':
        kernel = np.ones((3,3), np.uint8)
    if KERNEL_TYPE == 'closing':
        kernel = np.ones((3,3), np.uint8)
    
    return kernel
    
def getFilter(img, filter):
    if filter == 'closing':
        return cv2.morphologyEx(img, cv2.MORPH_CLOSE, getKernel('closing'), iterations=2)

    if filter == 'opening':
        return cv2.morphologyEx(img, cv2.MORPH_OPEN, getKernel('opening'), iterations=2)

    if filter == 'dilation':
        return cv2.dilate(img, getKernel('dilation'), iterations=2)

    if filter == 'combine':
        closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, getKernel('closing'), iterations=2)
        opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, getKernel('opening'), iterations=2)
        dilation = cv2.dilate(img, getKernel('dilation'), iterations=2)
        return dilation

def getBGSubtractor(BGS_TYPE):
    if BGS_TYPE == 'GMG':
        return cv2.bgsegm.createBackgroundSubtractorGMG()
    if BGS_TYPE == 'MOG':
        return cv2.bgsegm.createBackgroundSubtractorMOG()
    if BGS_TYPE == 'MOG2':
        return cv2.createBackgroundSubtractorMOG2()
    if BGS_TYPE == 'KNN':
        return cv2.createBackgroundSubtractorKNN()
    if BGS_TYPE == 'CNT':
        return cv2.bgsegm.createBackgroundSubtractorCNT()
    print("Detector inválido")
    sys.exit(1)


cap = cv2.VideoCapture(VIDEO_SOURCE)
minArea = 250
bg_subtractor = getBGSubtractor(BGS_TYPE)

def main():
    #while(cap.isOpened):
    while(True):
        try:
            ok, frame = cap.read()
            if not ok:
                print("Erro")
                break

            #frame = cv2.resize(frame, (0,0), fx=0.70, fy=0.70)

            bg_mask = bg_subtractor.apply(frame)
            bg_mask = getFilter(bg_mask, 'combine')
            bg_mask = cv2.medianBlur(bg_mask, 5) #Kernel medianBlur do OpenCV matriz de tamanho 5x5
            
            result = cv2.bitwise_and(frame, frame, mask=bg_mask) #Coloca a masck no vídeo original
            cv2.imshow('Frame', frame)
            cv2.imshow('Mask', bg_mask)
            cv2.imshow('Result', result)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        except:
            pass


main()