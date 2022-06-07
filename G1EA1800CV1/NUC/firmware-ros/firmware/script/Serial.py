#!/usr/bin/env python

import serial
import threading

import rospy
from std_msgs.msg import String
from std_msgs.msg import Bool
from std_msgs.msg import Int16
from std_msgs.msg import Float32
from std_msgs.msg import Float64
from std_msgs.msg import UInt32

import numpy as np
import time

#Publishers
pub_receive = rospy.Publisher("debug_serial", String, queue_size=10, tcp_nodelay=True) #Debug Serial

#Publishers para o AGV
pub_p15 = rospy.Publisher("agv_p15", Bool, queue_size=10, tcp_nodelay=True) #Controle Manual abaixa garfo
pub_p27 = rospy.Publisher("agv_p27", Bool, queue_size=10, tcp_nodelay=True) #Controle Manual levanta garfo
pub_p28 = rospy.Publisher("agv_p28", Bool, queue_size=10, tcp_nodelay=True) #Sinal Iniciar/Parar
pub_p29 = rospy.Publisher("agv_p29", Bool, queue_size=10, tcp_nodelay=True) #Sinal Interlock
pub_p30 = rospy.Publisher("agv_p30", Bool, queue_size=10, tcp_nodelay=True) #Sinal Freio pressionado
pub_p31 = rospy.Publisher("agv_p31", Bool, queue_size=10, tcp_nodelay=True) #Controle Manual Direita
pub_p32 = rospy.Publisher("agv_p32", Bool, queue_size=10, tcp_nodelay=True) #Controle Manual Esquerda
pub_p33 = rospy.Publisher("agv_p33", Bool, queue_size=10, tcp_nodelay=True) #Controle Manual acionado
pub_p34 = rospy.Publisher("agv_p34", Bool, queue_size=10, tcp_nodelay=True) #Sinal Emergência
pub_p35 = rospy.Publisher("agv_p35", Bool, queue_size=10, tcp_nodelay=True) #Encoder roda direita
pub_p36 = rospy.Publisher("agv_p36", Bool, queue_size=10, tcp_nodelay=True) #Encoder roda esquerda
pub_p37 = rospy.Publisher("agv_p37", Bool, queue_size=10, tcp_nodelay=True) #Encoder bomba hidráulica
pub_p38 = rospy.Publisher("agv_p38", Bool, queue_size=10, tcp_nodelay=True) #Sinal ultrassônico
pub_p39 = rospy.Publisher("agv_p39", Bool, queue_size=10, tcp_nodelay=True) #Scanner 2 Area 3
pub_p40 = rospy.Publisher("agv_p40", Bool, queue_size=10, tcp_nodelay=True) #Scanner 1 Area 3
pub_p41 = rospy.Publisher("agv_p41", Bool, queue_size=10, tcp_nodelay=True) #Scanner 2 Area 1
pub_p42 = rospy.Publisher("agv_p42", Bool, queue_size=10, tcp_nodelay=True) #Scanner 2 Area 2
pub_p43 = rospy.Publisher("agv_p43", Bool, queue_size=10, tcp_nodelay=True) #Scanner 1 Area 2
pub_p44 = rospy.Publisher("agv_p44", Bool, queue_size=10, tcp_nodelay=True) #Scanner 1 Area 1

pub_p106= rospy.Publisher("agv_p106", Int16, queue_size=10, tcp_nodelay=True) #Voltímetro interno
pub_p19 = rospy.Publisher("agv_p19", Int16, queue_size=10, tcp_nodelay=True) #Sinal Encoder direção
pub_p20 = rospy.Publisher("agv_p20", Int16, queue_size=10, tcp_nodelay=True)  #Sinal Encoder garfo
pub_p21 = rospy.Publisher("agv_p21", Int16, queue_size=10, tcp_nodelay=True) #Voltímetro bateria

pub_Serial_RCV = rospy.Publisher("Serial_RCV", Bool, queue_size=10, tcp_nodelay=True)
pub_agv_encoder_dist_count = rospy.Publisher("agv_encoder_dist_count", UInt32, queue_size=10, tcp_nodelay=True)
pub_agv_encoder = rospy.Publisher("agv_encoder", Float32, queue_size=10, tcp_nodelay=True)

P4_state = False    #Aciona Buzzer
P5_state = False    #Aciona Frente
P6_state = False    #Aciona Reverso
P7_state = False    #Aciona Segurança Acelerador
P8_state = False    #Aciona Buzina
P9_state = False    #Aciona Freio

P12_state = False   #Aciona Desliga Equipamento
P13_state = False   #Desliga Temporizado
P14_state = False   #Habilita Movimentação

P51_state = False   #Scanner Seleção 4 Área
P52_state = False   #Scanner Seleção 3 Área
P53_state = False   #Scanner Seleção 2 Área
P54_state = False   #Scanner Seleção 1 Área

encoder_dist_zerar_state = False

P45_state = 0   #PWM Acelerador
P46_state = 0   #PWM Servo Controle Elevação
P47_state = 0   #Led Vermelho
P48_state = 0   #Led Verde
P49_state = 0   #Led Azul
P50_state = 0 

volante = 0

countTotal = 0
ser = 0

send = False
send_size = 0

vet_bool1 = [False]*8
vet_bool2 = [False]*8
vet_bool3 = [False]*8

vet_float = [0.0]*2
vetIint = [0]*10
vetIlong = [0]*3
vetBytes = [0]*10
bool_array = [False]*24

Send_vet_float = [0.0]*2
Send_vetIint = [0]*10
Send_vetIlong = [0]*3
Send_vetBytes = [0]*10
Send_bool_array = [False]*24

con_pkg = 0

con_except = 0
reconectar = False

try:
    #time.sleep(10)
    ser = serial.Serial("/dev/ttyCentral", 115200, parity = serial.PARITY_NONE, stopbits = 1) #antes: /dev/ttyACM0
    #print("Conectando...")
except Exception as ex:
    print("Erro abrindo comunicacao serial: ")
    print(ex)
    
#Serial
write_data = [0]*54 #+4 de metadados
receive_data = [0]*9000

receive_data_aux = [0]*57
receive_pos = 0


def tentar_reconexao():
    global con_except, reconectar
    try:
        #time.sleep(10)
        ser = serial.Serial("/dev/ttyCentral", 115200, parity = serial.PARITY_NONE, stopbits = 1) #antes: /dev/ttyACM0
        con_except = 0
        reconectar = False
        #print("Conectando...")
    except Exception as ex:
        print("Erro abrindo comunicacao serial: ")
        print(ex)


def convertIntToBytes(val):
    r = [0]*2
    r[0] = val.to_bytes(2, byteorder='big' , signed=True)[1]
    r[1] = val.to_bytes(2, byteorder='big' , signed=True)[0]
    return r
	
def convertFloatToBytes(val):
    return np.array(val, dtype=np.float32).tobytes()
	
def convertLongToBytes(val):
    return np.array(val, dtype=np.int32).tobytes()

def convertBytestoLong(byte1, byte2, byte3, byte4):
    data_bytes = np.array([byte1, byte2, byte3, byte4], dtype=np.uint8)
    data_as_float = data_bytes.view(dtype=np.int32)
    return ((data_as_float[0]))

def convertBytestoInt(byte1, byte2):
    data_bytes = np.array([byte1, byte2], dtype=np.uint8)
    data_as_float = data_bytes.view(dtype=np.int16)
    return ((data_as_float[0]))
    
def convertBytestoInt8(byte1):
    data_bytes = np.array([byte1], dtype=np.uint8)
    data_as_float = data_bytes.view(dtype=np.int8)
    return ((data_as_float[0]))
    
def convertBytestoFloat(byte1,byte2,byte3,byte4):
    bytesFloat1 = [0]*4
    bytesFloat1[0] =  byte1
    bytesFloat1[1] =  byte2
    bytesFloat1[2] =  byte3
    bytesFloat1[3] =  byte4
    
    
    data_bytes = np.array(bytesFloat1, dtype=np.uint8)
    data_as_float = data_bytes.view(dtype=np.float32)
    
    return data_as_float[0]
	
def convertBitToInt(b1, b2, b3, b4, b5, b6, b7, b8):
    val = 0
    if(b1):
        val += 1	
    if(b2):
        val += 2
    if(b3):
        val += 4
    if(b4):
        val += 8
    if(b5):
        val += 16
    if(b6):
        val += 32
    if(b7):
        val += 64
    if(b8):
        val += 128
    
    return val
	
    
def convertBit(val):
    aux = [False]*8 
    
    strVet = bin(val)
    
    #print(val)
    #print(strVet)
    

    for i, c in enumerate(strVet):
        if(i > 1):
            if(len(strVet) > 9):
                if(i==2):
                    if(c == '1'):
                        aux[7] = True
                if(i==3):
                    if(c == '1'):
                        aux[6] = True
                if(i==4):
                    if(c == '1'):
                        aux[5] = True
                if(i==5):
                    if(c == '1'):
                        aux[4] = True
                if(i==6):
                    if(c == '1'):
                        aux[3] = True
                if(i==7):
                    if(c == '1'):
                        aux[2] = True
                if(i==8):
                    if(c == '1'):
                        aux[1] = True
                if(i==9):
                    if(c == '1'):
                        aux[0] = True
                
            elif(len(strVet) > 8):
            
                if(i==2):
                    if(c == '1'):
                        aux[6] = True
                if(i==3):
                    if(c == '1'):
                        aux[5] = True
                if(i==4):
                    if(c == '1'):
                        aux[4] = True
                if(i==5):
                    if(c == '1'):
                        aux[3] = True
                if(i==6):
                    if(c == '1'):
                        aux[2] = True
                if(i==7):
                    if(c == '1'):
                        aux[1] = True
                if(i==8):
                    if(c == '1'):
                        aux[0] = True
                
            
            elif(len(strVet) > 7):
            
                if(i==2):
                    if(c == '1'):
                        aux[5] = True
                if(i==3):
                    if(c == '1'):
                        aux[4] = True
                if(i==4):
                    if(c == '1'):
                        aux[3] = True
                if(i==5):
                    if(c == '1'):
                        aux[2] = True
                if(i==6):
                    if(c == '1'):
                        aux[1] = True
                if(i==7):
                    if(c == '1'):
                        aux[0] = True
                
            
            elif(len(strVet) > 6):
            
                if(i==2):
                    if(c == '1'):
                        aux[4] = True
                if(i==3):
                    if(c == '1'):
                        aux[3] = True
                if(i==4):
                    if(c == '1'):
                        aux[2] = True
                if(i==5):
                    if(c == '1'):
                        aux[1] = True
                if(i==6):
                    if(c == '1'):
                        aux[0] = True
                
            
            elif(len(strVet) > 5):
            
                if(i==2):
                    if(c == '1'):
                        aux[3] = True
                if(i==3):
                    if(c == '1'):
                        aux[2] = True
                if(i==4):
                    if(c == '1'):
                        aux[1] = True
                if(i==5):
                    if(c == '1'):
                        aux[0] = True
                        
            elif(len(strVet) > 4):
            
                if(i==2):
                    if(c == '1'):
                        aux[2] = True
                if(i==3):
                    if(c == '1'):
                        aux[1] = True
                if(i==4):
                    if(c == '1'):
                        aux[0] = True
         
                
            
            elif(len(strVet) > 3):
            
                if(i==2):
                    if(c == '1'):
                        aux[1] = True
                if(i==3):
                    if(c == '1'):
                        aux[0] = True
            
          
            else:
            
                if(i==2):
                    if(c == '1'):
                        aux[0] = True
                
            
                
            
           # print (c)
        
        
    
    
    return aux

pkg_end = b'\x0d'
pkg_size = 57
pkg_init_1 = b'\xFF'
pkg_init_2 = b'\xFE'
valTeste = False
init1 = 0
init2 = 0
ckaux1 = 0
ckaux2 = 0
def read_serial():
    global ser, send, countTotal, modo_erro, int_modo_erro, send_size
    global receive_data, receive_pos, bool_array, valTeste, init1, init2, ckaux1, ckaux2, receive_data_aux
    global vet_bool1, vet_bool2, vet_bool3, vet_bool4, vet_bool5, vet_bool6, vet_bool7, vetIint, vetIlong, vetBytes, vet_float
    #data = ser.read()

    try:
        rodou = False
        if(ser.inWaiting() <= 0):
            time.sleep(0.01)
        while (ser.inWaiting() > 0):
            for data in ser.read():
                
                data = data&0xff
                #print(converte)
                
                
              
                
                receive_data[receive_pos] = data
                receive_pos = receive_pos + 1           
                if(data == 13 and receive_pos >= pkg_size):
                    i = receive_pos-pkg_size
                    
                    countTotal+=1
                    
                    #if valTeste == True:
                        #print("ERR - ")
                        #print(countTotal)
                                    

                   # else:
                   #     print("OK")
                        
                   
           
                    valTeste = True
                  
                    init1 = receive_data[receive_pos - pkg_size]
                    init2 = receive_data[receive_pos - pkg_size +1]
          
                    if(receive_pos >= 57 and receive_data[receive_pos - pkg_size] == 255 and receive_data[receive_pos - pkg_size +1] == 254):
                        #print('Parte 2')
                        ck = 0
                        ck2 = 0
                        for number in range(receive_pos - pkg_size, receive_pos - 2):
                            ck2 += receive_data[number]

                        ck2 = ck2&0xff
                        
                        rodou = True
                        #print("a:"+str(ck2))
                        #print("b:"+str(receive_data[receive_pos -2]))
                        if(ck2 == receive_data[receive_pos -2]&0xff):
                            #Validou tudo
                            
                           
                            #Bool
                            bool_1 = receive_data[receive_pos - 57 + 2]
                            bool_2 = receive_data[receive_pos - 57 + 3]
                            bool_3 = receive_data[receive_pos - 57 + 4]

                            bool_array[0:7] = (convertBit(bool_1))
                            bool_array[8:15] = (convertBit(bool_2))
                            bool_array[16:23] = (convertBit(bool_3))
                            
                            #Float
                            vet_float[0] = convertBytestoFloat(receive_data[(receive_pos - 57 + 5)], receive_data[(receive_pos - 57 + 6)], receive_data[(receive_pos - 57 + 7)], receive_data[(receive_pos - 57 + 8)])
                            vet_float[1] = convertBytestoFloat(receive_data[(receive_pos - 57 + 9)], receive_data[(receive_pos - 57 + 10)], receive_data[(receive_pos - 57 + 11)], receive_data[(receive_pos - 57 + 12)])
                            
                            #Long
                            vetIlong[0] = convertBytestoLong(receive_data[(receive_pos - 57 + 13)], receive_data[(receive_pos - 57 + 14)], receive_data[(receive_pos - 57 + 15)], receive_data[(receive_pos - 57 + 16)])
                            vetIlong[1] = convertBytestoLong(receive_data[(receive_pos - 57 + 17)], receive_data[(receive_pos - 57 + 18)], receive_data[(receive_pos - 57 + 19)], receive_data[(receive_pos - 57 + 20)])
                            vetIlong[2] = convertBytestoLong(receive_data[(receive_pos - 57 + 21)], receive_data[(receive_pos - 57 + 22)], receive_data[(receive_pos - 57 + 23)], receive_data[(receive_pos - 57 + 24)])
                         
                            #Bytes
                            vetBytes[0] = receive_data[(receive_pos - 57 + 25)]
                            vetBytes[1] = receive_data[(receive_pos - 57 + 26)]
                            vetBytes[2] = receive_data[(receive_pos - 57 + 27)]
                            vetBytes[3] = receive_data[(receive_pos - 57 + 28)]
                            vetBytes[4] = receive_data[(receive_pos - 57 + 29)]
                            vetBytes[5] = receive_data[(receive_pos - 57 + 30)]
                            vetBytes[6] = receive_data[(receive_pos - 57 + 31)]
                            vetBytes[7] = receive_data[(receive_pos - 57 + 32)]
                            vetBytes[8] = receive_data[(receive_pos - 57 + 33)]
                            vetBytes[9] = receive_data[(receive_pos - 57 + 34)]
                            

                            vetIint[0] = convertBytestoInt(receive_data[(receive_pos - 57 + 35)], receive_data[(receive_pos - 57 + 36)])
                            vetIint[1] = convertBytestoInt(receive_data[(receive_pos - 57 + 37)], receive_data[(receive_pos - 57 + 38)])
                            vetIint[2] = convertBytestoInt(receive_data[(receive_pos - 57 + 39)], receive_data[(receive_pos - 57 + 40)])
                            vetIint[3] = convertBytestoInt(receive_data[(receive_pos - 57 + 41)], receive_data[(receive_pos - 57 + 42)])
                            vetIint[4] = convertBytestoInt(receive_data[(receive_pos - 57 + 43)], receive_data[(receive_pos - 57 + 44)])
                            vetIint[5] = convertBytestoInt(receive_data[(receive_pos - 57 + 45)], receive_data[(receive_pos - 57 + 46)])
                            vetIint[6] = convertBytestoInt(receive_data[(receive_pos - 57 + 47)], receive_data[(receive_pos - 57 + 48)])
                            vetIint[7] = convertBytestoInt(receive_data[(receive_pos - 57 + 49)], receive_data[(receive_pos - 57 + 50)])
                            vetIint[8] = convertBytestoInt(receive_data[(receive_pos - 57 + 51)], receive_data[(receive_pos - 57 + 52)])
                            vetIint[9] = convertBytestoInt(receive_data[(receive_pos - 57 + 53)], receive_data[(receive_pos - 57 + 54)])
                            
                            
                            send = True
                            
                            send_size = 0;

                            
                            receive_pos = 0
                            
                            pub_Serial_RCV.publish(True)
                            
                            valTeste = False
                            printer2 = "DATA: "
                            
                            if(ser.inWaiting() <= 0):
                                time.sleep(0.02)
                            #print("CHEGOU B\n")
                        else:
                            pub_receive.publish("FALHA CK")
                           
                    else:
                        #modo_erro = True
                        printer = "DATA: "
                        if(receive_pos >= 57):
                            for number in range(receive_pos - pkg_size, receive_pos):
                                printer += " " + str(receive_data[number])
                            pub_receive.publish(printer)
                        pub_receive.publish("FALHA 1, Tamanho: " + str((receive_pos - pkg_size)) + " receive_pos: " + str(receive_pos) + " init 1:" + str(receive_data[receive_pos - 57]) ) 
                        
                        
                        
                
                if(receive_pos >= 9000):
                    pub_receive.publish("RST")
                    receive_pos = 0
                    modo_erro = True
                
    except Exception as ex:
        # print ("Erro __main__ Serial: " + str(ex))
        pub_receive.publish("Erro read_serial: " + str(ex))
     

def write_cmd():
    global P45_state, P46_state, P47_state, P48_state, P49_state, Send_bool_array, Send_vetBytes, Send_vetIint, volante
    global P3_state, P4_state, P5_state, P6_state, P7_state, P8_state, P9_state, P12_state, P13_state, P51_state, P52_state, P53_state, P54_state, encoder_dist_zerar_state
    
    Send_vetBytes[0] = P45_state        #OK
    Send_vetBytes[1] = P46_state        #OK
    Send_vetBytes[2] = P47_state        #OK
    Send_vetBytes[3] = P48_state        #OK
    Send_vetBytes[4] = P49_state        #OK
    Send_vetBytes[5] = P50_state        #OK
    
    Send_bool_array[0] = P4_state       #OK
    Send_bool_array[1] = P5_state       #OK
    Send_bool_array[2] = P6_state       #OK
    Send_bool_array[3] = P7_state       #OK
    Send_bool_array[4] = P8_state       #OK
    Send_bool_array[5] = P9_state       #OK
    Send_bool_array[6] = P12_state      #OK
    Send_bool_array[7] = P13_state      #OK
    Send_bool_array[8] = P14_state      #OK
    Send_bool_array[9] = P51_state      #OK
    Send_bool_array[10] = P52_state     #OK
    Send_bool_array[11] = P53_state     #OK
    Send_bool_array[12] = P54_state     #OK
    
    Send_bool_array[13] = encoder_dist_zerar_state #Verificar
    
    Send_vetIint[0] = volante
        
def write_serial():
    global ser, Send_vet_float, Send_vetIint, Send_vetIlong, Send_vetBytes, Send_bool_array
	
    pk = [0]*57
	
    pk[0] = 255&0xFF
    pk[1] = 254&0xFF
    
    #Bool
    pk[2] = convertBitToInt(Send_bool_array[0], Send_bool_array[1], Send_bool_array[2], Send_bool_array[3], Send_bool_array[4], Send_bool_array[5], Send_bool_array[6], Send_bool_array[7])
    pk[3] = convertBitToInt(Send_bool_array[8], Send_bool_array[9], Send_bool_array[10], Send_bool_array[11], Send_bool_array[12], Send_bool_array[13], Send_bool_array[14], Send_bool_array[15])	
    pk[4] = convertBitToInt(Send_bool_array[16], Send_bool_array[17], Send_bool_array[18], Send_bool_array[19], Send_bool_array[20], Send_bool_array[21], Send_bool_array[22], Send_bool_array[23])
    
    #Float
    pk[5:8] = convertFloatToBytes(Send_vet_float[0])
    pk[9:12] = convertFloatToBytes(Send_vet_float[1])
   
    #Long
    pk[13:16] = convertLongToBytes(Send_vetIlong[0])
    pk[17:20] = convertLongToBytes(Send_vetIlong[1])
    pk[21:24] = convertLongToBytes(Send_vetIlong[2])
    
    #Bytes
    for i in range(10):
        pk[25 + i] = Send_vetBytes[i]&0xFF
    
    #Int
    pk[35:36] = convertIntToBytes(Send_vetIint[0])
    pk[37:38] = convertIntToBytes(Send_vetIint[1])
    pk[39:40] = convertIntToBytes(Send_vetIint[2])
    pk[41:42] = convertIntToBytes(Send_vetIint[3])
    pk[43:44] = convertIntToBytes(Send_vetIint[4])
    pk[45:46] = convertIntToBytes(Send_vetIint[5])
    pk[47:48] = convertIntToBytes(Send_vetIint[6])
    pk[49:50] = convertIntToBytes(Send_vetIint[7])
    pk[51:52] = convertIntToBytes(Send_vetIint[8])
    pk[53:54] = convertIntToBytes(Send_vetIint[9])
    
	
    ck = 0
    for n in range(55):
        ck += pk[n]
	
    pk[55] = ck&0xFF
    pk[56] = 13&0xFF
	
    ser.write(pk)
       

def thread_delay():
    while not rospy.is_shutdown():
        read_serial()
        
        

def p3_callback(data):
    global P3_state
    P3_state = data.data
    
def p4_callback(data):
    global P4_state
    P4_state = data.data
    
def p5_callback(data):
    global P5_state
    P5_state = data.data
    
def p6_callback(data):
    global P6_state
    P6_state = data.data
    
def p7_callback(data):
    global P7_state
    P7_state = data.data
    
def p8_callback(data):
    global P8_state
    P8_state = data.data
    
def p9_callback(data):
    global P9_state
    P9_state = data.data
    
def p12_callback(data):
    global P12_state
    P12_state = data.data
    
def p13_callback(data):
    global P13_state
    P13_state = data.data

def p14_callback(data):
    global P14_state
    P14_state = data.data    

    
def encoder_dist_zerar_callback(data):
    global encoder_dist_zerar_state
    encoder_dist_zerar_state = data.data
    
def p51_callback(data):
    global P51_state
    P51_state = data.data
def p52_callback(data):
    global P52_state
    P52_state = data.data
def p53_callback(data):
    global P53_state
    P53_state = data.data
def p54_callback(data):
    global P54_state
    P54_state = data.data
    
   
def p45_callback(data):
    global P45_state
    P45_state = data.data&0xFF
def p46_callback(data):
    global P46_state
    P46_state = data.data&0xFF
def p47_callback(data):
    global P47_state
    P47_state = data.data&0xFF
def p48_callback(data):
    global P48_state
    P48_state = data.data&0xFF
def p49_callback(data):
    global P49_state
    P49_state = data.data&0xFF
def p50_callback(data):
    global P50_state
    P50_state = data.data&0xFF


def Thread_logica():
    global send, prime_com, send_size, con_except, reconectar
    

    while not rospy.is_shutdown():
        
        if(reconectar):
            print("Reconectando...")
            tentar_reconexao()
            time.sleep(1)
        else:
        
            try:
                write_cmd()
                write_serial()

                if(send):
                    
                    send = False
                    
                    #Publica a cada 50ms            
                               
                    pub_agv_encoder_dist_count.publish(vetIlong[0])
                    pub_agv_encoder.publish(vet_float[0])
                   
                    pub_p15.publish(bool_array[0]) 
                    pub_p27.publish(bool_array[1])  
                    pub_p28.publish(bool_array[2])
                    pub_p29.publish(bool_array[3])
                    pub_p30.publish(bool_array[4])
                    pub_p31.publish(bool_array[5])
                    pub_p32.publish(bool_array[6])
                    pub_p33.publish(bool_array[7])
                    pub_p34.publish(bool_array[8])
                    pub_p35.publish(bool_array[9])
                    pub_p36.publish(bool_array[10])		
                    pub_p37.publish(bool_array[11])		
                    pub_p38.publish(bool_array[12])		
                    pub_p39.publish(bool_array[13])		
                    pub_p40.publish(bool_array[14])
                    pub_p41.publish(bool_array[15])
                    pub_p42.publish(bool_array[16])
                    pub_p43.publish(bool_array[17])
                    pub_p44.publish(bool_array[18])
                        
                    pub_p106.publish(vetIint[0])
                    pub_p19.publish(vetIint[1])
                    pub_p20.publish(vetIint[2])
                    pub_p21.publish(vetIint[3])
                    
                
                send_size += 1
                if(send_size > 5):
                    time.sleep(0.05)
                else:
                    time.sleep(0.05)
                    
            except Exception as ex:
                print ("Erro __main__ Serial: " + str(ex))
                if(con_except < 20):
                    con_except = con_except + 1
                else:
                    reconectar = True
                #pub_ros_debug.publish("Erro __main__ Serial: " + str(ex))
            
def agv_volante_callback(data):
    global volante
    volante = data.data
            
if __name__ == '__main__':
    rospy.init_node('Serial', anonymous=False)
    
    
    ####################################VETOR BOOL#########################################
	
    rospy.Subscriber("agv_p4", Bool, p4_callback, queue_size=1, buff_size=2**24) #2
    rospy.Subscriber("agv_p5", Bool, p5_callback, queue_size=1, buff_size=2**24) #3
    rospy.Subscriber("agv_p6", Bool, p6_callback, queue_size=1, buff_size=2**24) #4
    rospy.Subscriber("agv_p7", Bool, p7_callback, queue_size=1, buff_size=2**24) #5
    rospy.Subscriber("agv_p8", Bool, p8_callback, queue_size=1, buff_size=2**24) #6
    rospy.Subscriber("agv_p9", Bool, p9_callback, queue_size=1, buff_size=2**24) #7
    
    rospy.Subscriber("agv_p12", Bool, p12_callback, queue_size=1, buff_size=2**24) #8
    rospy.Subscriber("agv_p13", Bool, p13_callback, queue_size=1, buff_size=2**24) #9
    rospy.Subscriber("agv_p14", Bool, p14_callback, queue_size=1, buff_size=2**24) #10
    
    rospy.Subscriber("agv_p51", Bool, p51_callback, queue_size=1, buff_size=2**24) #11
    rospy.Subscriber("agv_p52", Bool, p52_callback, queue_size=1, buff_size=2**24) #12
    rospy.Subscriber("agv_p53", Bool, p53_callback, queue_size=1, buff_size=2**24) #13
    rospy.Subscriber("agv_p54", Bool, p54_callback, queue_size=1, buff_size=2**24) #14
    
    rospy.Subscriber("agv_encoder_dist_zerar", Bool, encoder_dist_zerar_callback, queue_size=1, buff_size=2**24) #15
    
    ########################################################################################
    
    
    ####################################VETOR Bytes#########################################
    
    rospy.Subscriber("agv_p45", Int16, p45_callback, queue_size=1, buff_size=2**24) #0
    rospy.Subscriber("agv_p46", Int16, p46_callback, queue_size=1, buff_size=2**24) #1
    rospy.Subscriber("agv_p47", Int16, p47_callback, queue_size=1, buff_size=2**24) #2
    rospy.Subscriber("agv_p48", Int16, p48_callback, queue_size=1, buff_size=2**24) #3
    rospy.Subscriber("agv_p49", Int16, p49_callback, queue_size=1, buff_size=2**24) #4
    rospy.Subscriber("agv_p50", Int16, p50_callback, queue_size=1, buff_size=2**24) #4
    
    rospy.Subscriber("agv_volante", Int16, agv_volante_callback, queue_size=1, buff_size=2**24) #4
    
    ########################################################################################

    rate = rospy.Rate(10) #1 vez a cada 50ms
    
    t1 = threading.Thread(target=thread_delay)
    t1.start()
    
    time.sleep(15)
    
    t2 = threading.Thread(target=Thread_logica)
    t2.start()
    
    print("INICIANDO")
    
    #time.sleep(10)
  
    while not rospy.is_shutdown():
       
        rate.sleep()