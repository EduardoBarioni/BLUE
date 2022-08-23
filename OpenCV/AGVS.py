import cv2
import numpy as np
import time

cv2.namedWindow("janela")
VIDEO_SOURCE = "rtsp://admin:SIBTKK@192.168.0.109/cam/realmonitor?channel=1&subtype=0" #REDE AGVS_escritório
VIDEO_SOURCE = "/home/user/AGVS repository/OpenCV/04.mp4"
VIDEO_SOURCE = "/home/user/AGVS repository/OpenCV/project_video.mp4"
#VIDEO_SOURCE = 6#VIDEO_SOURCE = "rtsp://admin:SIBTKK@192.168.55.116/cam/realmonitor?channel=1&subtype=0" #REDE AGVS_escritório
cap=cv2.VideoCapture(VIDEO_SOURCE)

BGS_TYPES = ["GMG", "MOG", "MOG2", "KNN", "CNT"]
BGS_TYPE = BGS_TYPES[2]

pos = [0, 0]

TEXT_COLOR = (0,255,0)
TRACKER_COLOR = (255,0,0)
FONT = cv2.FONT_HERSHEY_SIMPLEX
pTime = 0
cTime = 0

def posicao(img, frame):
    minArea = 250
    # encontra pontos que circundam regiões conexas (contour)
    contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    #print(contours)
    # se existir contornos
    if contours:
        # retornando a área do primeiro grupo de pixels brancos
        maxArea = cv2.contourArea(contours[0])
        contourMaxAreaId = 0
        i = 0
        # para cada grupo de pixels branco
        for cnt in contours:
            # procura o grupo com a maior área
            if maxArea < cv2.contourArea(cnt):
                maxArea = cv2.contourArea(cnt)
                contourMaxAreaId = i
            i += 1
        if maxArea > minArea:
            detectou = 1
        else:
            detectou = 0
        if detectou == 1:
            # achei o contorno com maior área em pixels
            cntMaxArea = contours[contourMaxAreaId]

            # retorna um retângulo que envolve o contorno em questão
            xRect, yRect, wRect, hRect = cv2.boundingRect(cntMaxArea)
            # centro do retangulo
            pos[0] = int(xRect+wRect/2) #X
            pos[1] = int(yRect+hRect/2) #Y

            # desenha o centro do retangulo
            cv2.circle(img, (pos[0], pos[1]), 5, (255, 255, 255), cv2.FILLED)
            cv2.circle(frame, (pos[0], pos[1]), 5, (0, 0, 255), cv2.FILLED)
            # desenha caixa envolvente com espessura 3
            cv2.rectangle(img, (xRect, yRect), (xRect + wRect, yRect + hRect), (255, 255, 255), 2)
            cv2.rectangle(frame, (xRect, yRect), (xRect + wRect, yRect + hRect), (0, 255, 0), 1)
            #Escreve a posição na imagem
            cv2.putText(frame, f'Pos (X, Y): {pos[0],pos[1]}', (int(pos[0]/2) , int(pos[1]-50)), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)

    return img, frame, pos

def getKernel(KERNEL_TYPE):
    if KERNEL_TYPE == 'dilation':
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    if KERNEL_TYPE == 'opening':
        kernel = np.ones((3, 3), np.uint8)
    if KERNEL_TYPE == 'closing':
        kernel = np.ones((3, 3), np.uint8)

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


def posicao(img, frame):
    minArea = 250
    # encontra pontos que circundam regiões conexas (contour)
    contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    # print(contours)
    # se existir contornos
    if contours:
        # retornando a área do primeiro grupo de pixels brancos
        maxArea = cv2.contourArea(contours[0])
        contourMaxAreaId = 0
        i = 0
        # para cada grupo de pixels branco
        for cnt in contours:
            # procura o grupo com a maior área
            if maxArea < cv2.contourArea(cnt):
                maxArea = cv2.contourArea(cnt)
                contourMaxAreaId = i
            i += 1
        if maxArea > minArea:
            detectou = 1
        else:
            detectou = 0
        if detectou == 1:
            # achei o contorno com maior área em pixels
            cntMaxArea = contours[contourMaxAreaId]

            # retorna um retângulo que envolve o contorno em questão
            xRect, yRect, wRect, hRect = cv2.boundingRect(cntMaxArea)
            # centro do retangulo
            pos[0] = int(xRect + wRect / 2)  # X
            pos[1] = int(yRect + hRect / 2)  # Y

            # desenha o centro do retangulo
            cv2.circle(img, (pos[0], pos[1]), 5, (255, 255, 255), cv2.FILLED)
            cv2.circle(frame, (pos[0], pos[1]), 5, (0, 0, 255), cv2.FILLED)
            # desenha caixa envolvente com espessura 3
            cv2.rectangle(img, (xRect, yRect), (xRect + wRect, yRect + hRect), (255, 255, 255), 2)
            cv2.rectangle(frame, (xRect, yRect), (xRect + wRect, yRect + hRect), (0, 255, 0), 1)
            # Escreve a posição na imagem
            cv2.putText(frame, f'Pos (X, Y): {pos[0], pos[1]}', (int(pos[0] / 2), int(pos[1] - 50)),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)

    return img, frame, pos
    # print(img.shape)
    # cy = int(int(img.shape[0])/2)
    # cx = int(int(img.shape[1])/2)
    # cv2.circle(img, (cx, cy), 5, (255, 255, 255), cv2.FILLED)
    # return img
    # cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),
    #               (bbox[2] + 20, bbox[3] + 20), (0, 255, 0), 2)
    # cv2.putText(img, f'Vol Set: {int(cVol)}', (400, 50), cv2.FONT_HERSHEY_COMPLEX,
    #            1, colorVol, 3)
    # branco = np.sum(img == 255)
    # print(branco)


# fourcc = cv2.VideoWriter_fourcc(*'DIVX')
# out = cv2.VideoWriter('/home/user/AGVS repository/BLUE/BLUE 2.0/reconhecimentos/Videos/output.avi', fourcc, 20.0, (640, 480))


def mause(pos):
    pass
cv2.createTrackbar("H_min", "janela" , 0, 180,mause)
cv2.createTrackbar("S_min", "janela" , 0, 255,mause)
cv2.createTrackbar("V_min", "janela" , 220, 255,mause)
cv2.createTrackbar("H_max", "janela" , 180, 180,mause)
cv2.createTrackbar("S_max", "janela" , 255, 255,mause)
cv2.createTrackbar("V_max", "janela" , 255, 255,mause)
while(cap.isOpened()):
    ret,frame1=cap.read()
    cv2.imshow("frame", frame1)
    h_min = cv2.getTrackbarPos("H_min", 'janela') #70
    s_min = cv2.getTrackbarPos("S_min", 'janela') #20
    v_min = cv2.getTrackbarPos("V_min", 'janela') #225
    h_max = cv2.getTrackbarPos("H_max", 'janela') #180
    s_max = cv2.getTrackbarPos("S_max", 'janela') #255
    v_max = cv2.getTrackbarPos("V_max", 'janela') #255

    frame = frame1
    # h_min = 0
    # s_min = 0
    # v_min = 220
    # h_max = 180
    # s_max = 255
    # v_max = 255

    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    maks=cv2.inRange(hsv,np.array([h_min,s_min,v_min]),np.array([h_max,s_max,v_max]))
    saida=cv2.bitwise_and(frame,frame,mask=maks)
    string = "H_min " + str(h_min)+" S_min "+str(s_min)+ " V_min "+str(v_min)
    string=string+" H_max " + str(h_max)+" S_max "+str(s_max)+ " V_max "+str(v_max)
    cv2.putText(saida, string, (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.45, (0, 0, 255))

    gray_image = cv2.cvtColor(saida, cv2.COLOR_BGR2GRAY)
    gray_image01 = cv2.cvtColor(gray_image, cv2.COLOR_BGR2RGB)

    x = gray_image.shape[1]
    y = gray_image.shape[0]
    #print(str(x) + "x" + str(y))

    # cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(gray_image, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 255), 3)

    # number_of_white_pix = np.sum(gray_image == 255)
    # number_of_black_pix = np.sum(gray_image == 0)
    #
    # print('Number of white pixels:', number_of_white_pix)
    # print('Number of black pixels:', number_of_black_pix)
    centro = x/2
    for j in range(int(y/2), y-1, 10):
        #print(f"---------------------------------------{j}---------------------------------------")
        pxd = centro
        pxe = centro
        auxe = 0
        auxd = 0
        pontod = 0
        pontoe = 0
        for i in range(1, int(centro), 1):
            pxd = pxd + 1
            pxe = pxe - 1
            if gray_image[j, int(pxd)] > 150 and auxd == 0:
                cv2.circle(gray_image01, (int(pxd), j), 2, (255, 0, 255))

                pontod = pxd
                auxd = 1
            if gray_image[j, int(pxe)] > 150 and auxe == 0:
                cv2.circle(gray_image01, (int(pxe), j), 2, (255, 0, 255))
                pontoe = pxe
                auxe = 1


            if auxd == 1 and auxe == 1:
                print(f'pontod: {pontod}')
                print(f'pontoe: {pontoe}')
                cv2.line(gray_image01,(int(pontoe),j),(int(pontod),j),(255, 0, 0))
                i = int(centro / 2)

                print('-----------------------------------entrou--------------------------------------')

    cv2.line(gray_image01, (int(x / 2), 0), (int(x / 2), y), (255, 255, 0))
    img, frame, pos = posicao(gray_image, gray_image)

    cv2.imshow("img", img)
    cv2.imshow("frame", frame)
    #print(pos)
    cv2.imshow("janela",saida)
    cv2.imshow("gray_image", gray_image)
    cv2.imshow("gray_image01", gray_image01)
    k = cv2.waitKey(30)
    if k ==ord("q"):
        break