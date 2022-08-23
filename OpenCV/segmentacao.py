import cv2
import time
import numpy as np
cv2.namedWindow("janela")
VIDEO_SOURCE = "rtsp://admin:SIBTKK@192.168.0.109/cam/realmonitor?channel=1&subtype=0" #REDE AGVS_escritório
#VIDEO_SOURCE = 0
VIDEO_SOURCE = "/home/user/AGVS repository/OpenCV/04.mp4"
VIDEO_SOURCE = "/home/user/AGVS repository/OpenCV/project_video.mp4"
#VIDEO_SOURCE = 0
cap=cv2.VideoCapture(VIDEO_SOURCE)
pTime = 0
cTime = 0


def mause(pos):
    pass
cv2.createTrackbar("H_min", "janela" , 0, 180,mause)
cv2.createTrackbar("S_min", "janela" , 0, 255,mause)
cv2.createTrackbar("V_min", "janela" , 220, 255,mause)
cv2.createTrackbar("H_max", "janela" , 180, 180,mause)
cv2.createTrackbar("S_max", "janela" , 255, 255,mause)
cv2.createTrackbar("V_max", "janela" , 255, 255,mause)
while(cap.isOpened()):
    ret,frame=cap.read()

    h_min = cv2.getTrackbarPos("H_min", 'janela') #70
    s_min = cv2.getTrackbarPos("S_min", 'janela') #20
    v_min = cv2.getTrackbarPos("V_min", 'janela') #225
    h_max = cv2.getTrackbarPos("H_max", 'janela') #180
    s_max = cv2.getTrackbarPos("S_max", 'janela') #255
    v_max = cv2.getTrackbarPos("V_max", 'janela') #255

    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    maks=cv2.inRange(hsv,np.array([h_min,s_min,v_min]),np.array([h_max,s_max,v_max]))
    saida=cv2.bitwise_and(frame,frame,mask=maks)
    string = "H_min " + str(h_min)+" S_min "+str(s_min)+ " V_min "+str(v_min)
    string=string+" H_max " + str(h_max)+" S_max "+str(s_max)+ " V_max "+str(v_max)
    cv2.putText(saida, string, (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.45, (0, 0, 255))

    gray_image = cv2.cvtColor(saida, cv2.COLOR_BGR2GRAY)


    x = gray_image.shape[1]
    y = gray_image.shape[0]
    print(str(x) + "x" + str(y))
    cv2.line(gray_image, (int(x / 2), 0), (int(x / 2), y), (255, 0, 255))
    # cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(gray_image, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 255), 3)

    centro = x/2
    for j in range(y):
        for i in range(int(centro)):
            pxd = centro + 1
            pxe = centro - 1
            if pxd == 0:
                cv2.circle(gray_image,(int(pxd),j),1,(255,0,255))
            if pxe == 0:
                gray_image = cv2.circle(gray_image,(int(pxe), j), 1, (255, 0, 255))







    cv2.imshow("janela",saida)
    cv2.imshow("gray_image", gray_image)

    k = cv2.waitKey(30)
    if k ==ord("q"):
        break