import cv2
import numpy as np
import sys
cv2.namedWindow("janela")

TEXT_COLOR = (0,255,0)
TRACKER_COLOR = (255,0,0)
FONT = cv2.FONT_HERSHEY_SIMPLEX
#VIDEO_SOURCE = "test_videos/solidWhiteRight.mp4"
#VIDEO_SOURCE = "project_video.mp4"
#VIDEO_SOURCE = "http://192.168.55.116:4747/video"
#VIDEO_SOURCE = "rtsp://admin:SIBTKK@192.168.55.116/cam/realmonitor?channel=1&subtype=0" #REDE AGVS
VIDEO_SOURCE = "rtsp://admin:SIBTKK@192.168.15.77/cam/realmonitor?channel=1&subtype=0" #REDE AGVS_escritório
#VIDEO_SOURCE = 0

LimiarBinarizacao = 125       #este valor eh empirico. Ajuste-o conforme sua necessidade 
AreaContornoLimiteMin = 5000  #este valor eh empirico. Ajuste-o conforme sua necessidade 

def mause(pos):
    pass
cv2.createTrackbar("H_min", "janela" , 70, 180,mause)
cv2.createTrackbar("S_min", "janela" , 20, 255,mause)
cv2.createTrackbar("V_min", "janela" , 200, 255,mause)
cv2.createTrackbar("H_max", "janela" , 180, 180,mause)
cv2.createTrackbar("S_max", "janela" , 255, 255,mause)
cv2.createTrackbar("V_max", "janela" , 255, 255,mause)

## AMARELO
# cv2.createTrackbar("H_min", "janela" , 12, 180,mause)
# cv2.createTrackbar("S_min", "janela" , 42, 255,mause)
# cv2.createTrackbar("V_min", "janela" , 192, 255,mause)
# cv2.createTrackbar("H_max", "janela" , 106, 180,mause)
# cv2.createTrackbar("S_max", "janela" , 255, 255,mause)
# cv2.createTrackbar("V_max", "janela" , 255, 255,mause)

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
        opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, getKernel('opening'), iterations=8)
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

def getCor(frame):
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

    return saida



def TrataImagem(img):
    #obtencao das dimensoes da imagem
    height = np.size(img,0)
    width= np.size(img,1)
    QtdeContornos = 0
    DirecaoASerTomada = 0
     
    #tratamento da imagem
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    FrameBinarizado = cv2.threshold(gray,LimiarBinarizacao,255,cv2.THRESH_BINARY)[1]
    FrameBinarizado = cv2.dilate(FrameBinarizado,None,iterations=2)
    #FrameBinarizado = cv2.bitwise_not(FrameBinarizado)
     
    #descomente as linhas abaixo se quiser ver o frame apos binarizacao, dilatacao e inversao de cores
    cv2.imshow('F.B.',FrameBinarizado)
    #cv2.waitKey(10)

 
    cnts, _ = cv2.findContours(FrameBinarizado.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(img,cnts,-1,(255,0,255),3)
 
    for c in cnts:
        #se a area do contorno capturado for pequena, nada acontece
        if cv2.contourArea(c) < AreaContornoLimiteMin:
            continue
        else:
            QtdeContornos = QtdeContornos + 1
 
        #obtem coordenadas do contorno (na verdade, de um retangulo que consegue abrangir todo ocontorno) e
        #realca o contorno com um retangulo.
        (x, y, w, h) = cv2.boundingRect(c)   #x e y: coordenadas do vertice superior esquerdo
                                             #w e h: respectivamente largura e altura do retangulo
 
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
     
        #determina o ponto central do contorno e desenha um circulo para indicar
        CoordenadaXCentroContorno = (x+x+w)/2
        CoordenadaYCentroContorno = (y+y+h)/2
        PontoCentralContorno = (CoordenadaXCentroContorno,CoordenadaYCentroContorno)
        try:
            cv2.circle(img, PontoCentralContorno, 1, (0, 0, 0), 5)
        except:
            pass
         
        DirecaoASerTomada = CoordenadaXCentroContorno - (width/2)   #em relacao a linha central
      
    #output da imagem
    #linha em azul: linha central / referencia
    #linha em verde: linha que mostra distancia entre linha e a referencia
    try:
        cv2.line(img,(width/2,0),(width/2,height),(255,0,0),2)
    except:
        pass
     
    if (QtdeContornos > 0):
        try:
            cv2.line(img,PontoCentralContorno,(width/2,CoordenadaYCentroContorno),(0,255,0),1)
        except:
            pass
     
    

    cv2.imshow('Analise de rota',img)
    #cv2.waitKey(10)

    return DirecaoASerTomada, QtdeContornos

cap = cv2.VideoCapture(VIDEO_SOURCE)
minArea = 250
bg_subtractor = getBGSubtractor(BGS_TYPE)

def main():
    while(cap.isOpened):
        ok, frame = cap.read()
        if not ok:
            print("Erro")
            break
        #frame = cv2.resize(frame, (0,0), fx=0.70, fy=0.70)

        bg_mask = getCor(frame)
        #bg_mask = bg_subtractor.apply(frame)

        bg_mask = getFilter(bg_mask, 'combine')
        bg_mask = cv2.medianBlur(bg_mask, 5) #Kernel medianBlur do OpenCV matriz de tamanho 5x5
        



        cv2.imshow("janela", bg_mask)
        #result = cv2.bitwise_and(frame, frame, mask=bg_mask) #Coloca a masck no vídeo original
        cv2.imshow('Frame', frame)
        #cv2.imshow('Mask', bg_mask)

        Direcao,QtdeLinhas = TrataImagem(bg_mask)
        if (QtdeLinhas == 0):
            print("Nenhuma linha encontrada. O robo ira parar.")
            #continue
        if (Direcao > 0):
            print("Distancia da linha de referencia: "+str(abs(Direcao))+" pixels a direita")
        if (Direcao < 0):
            print("Distancia da linha de referencia: "+str(abs(Direcao))+" pixels a esquerda")  
        if (Direcao == 0):
            print("Exatamente na linha de referencia!") 


        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


main()