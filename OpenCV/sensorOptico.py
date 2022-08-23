import cv2
#VIDEO_SOURCE = "rtsp://admin:SIBTKK@192.168.15.6/cam/realmonitor?channel=1&subtype=0" #REDE AGVS_escritório
VIDEO_SOURCE = "rtsp://admin:SIBTKK@192.168.55.116/cam/realmonitor?channel=1&subtype=0" #REDE AGVS
VIDEO_SOURCE = 6
#VIDEO_SOURCE = "rtsp://admin:ThomazRsMBP2652@192.168.55.188/cam/realmonitor?channel=1&subtype=0" #REDE AGVS
VIDEO_SOURCE = "/home/user/AGVS repository/OpenCV/filename.avi"

import mediapipe as mp
import time

cap = cv2.VideoCapture(VIDEO_SOURCE)

pTime = 0
cTime = 0

while True:
    success, img = cap.read()
    if success:
        # (b, g, r) = img[0,0]
        # print('O pixel (0, 0) tem as seguintes cores:')
        # print('Vermelho:', r)#, 'Verde:', g, 'Azul:', b)
        #print(img)
        # x = img.shape[1]
        # y = img.shape[0]
        #img = cv2.resize(img, (640, int(640*y/x)), interpolation=cv2.INTER_NEAREST)
        #imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)



        #print(str(x) + "x" + str(y))
        #cv2.line(img, (int(x/2),0),(int(x/2),y),(255,0,255))
        #cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)







        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        cv2.imshow("Image", img)
    cv2.waitKey(100)