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

altura_set = 10
posicionar = False

pub_G1EA1800CV1_garfo_acionar = rospy.Publisher("G1EA1800CV1_garfo_acionar", Int16, queue_size=10, tcp_nodelay=True) 

pub_garfo_ok = rospy.Publisher("garfo_ok", Bool, queue_size=10, tcp_nodelay=True)


altura_Atual = 0;

kp = 90
ki = 30
kd = 0

erro = 0
erro_old = 0
proporcional = 0
integral = 0
derivativo = 0
lim_integral = 20
controle = 0
reset = 0
ok = 0

def PID(valorLido, valorSetado):
    global erro, erro_old, kp, ki, kd
    global proporcional, integral, derivativo, controle, reset
    
    
    
    erro = ((valorSetado - valorLido) * -1) / 100
    proporcional = erro * kp
    integral = integral + (erro * ki)
    derivativo = (erro - erro_old) * kd
    
    erro_old = erro
    
    if(integral >= lim_integral):
        integral = lim_integral
    
    if(integral <= -lim_integral):
        integral = -lim_integral
    
    #Zerar Integral
    if(valorLido > (valorSetado-3) and valorLido < (valorSetado+3)):
        integral = 0
    
    controle = (proporcional + integral + derivativo) *-1
    
    
    
    if((valorLido - valorSetado) > 512 or (valorLido - valorSetado) < -512):
        if(controle > 7):
            controle = 7
            
        if(controle < -7):
            controle = -7
            
        reset = 0
    
    else:
    
        reset = reset + 1
        
        if(reset < 20):
            controle = 0
    
        if(controle > 7):
            controle = 7
            
        if(controle < -7):
            controle = -7

def garfo_altura_set_callback(data):
    global altura_set, posicionar
    altura_set = data.data
    posicionar = True
 
def garfo_posicionar_callback(data):
    global posicionar
    posicionar = data.data

def Thread_logica():
    global altura_set, posicionar, ok, altura_Atual

    while not rospy.is_shutdown():
        try:
               
            if posicionar:
                
                PID(altura_Atual, altura_set)
                pwm = 45 + controle
                
                
                
                print("altura_Atual: " + str(altura_Atual) + " altura_set: " + str(altura_set) + " pwm: " + str(pwm))
                if(altura_Atual > (altura_set-5) and altura_Atual < (altura_set+5)):
                    ok = ok + 1
       
                    if(ok > 20):
                        print("Finalizado")
                        posicionar = False
                else:
                    ok = 0
                
                pub_G1EA1800CV1_garfo_acionar.publish(int(pwm))
                pub_garfo_ok.publish(False)
                
            else:
                pub_G1EA1800CV1_garfo_acionar.publish(45)
                pub_garfo_ok.publish(True)
                ok = 0
                
            time.sleep(0.05)
                
        except Exception as ex:
            print ("Erro __main__ Garfo: " + str(ex))
            #pub_ros_debug.publish("Erro __main__ Serial: " + str(ex))
            
            
def agv_p20_callback(data):
    global altura_Atual
    altura_Atual = data.data

            
if __name__ == '__main__':
    rospy.init_node('Garfo', anonymous=False)
    
    rospy.Subscriber("garfo_altura_set", Int16, garfo_altura_set_callback, queue_size=1, buff_size=2*24)
    rospy.Subscriber("garfo_posicionar", Bool, garfo_posicionar_callback, queue_size=1, buff_size=2*24)
    rospy.Subscriber("agv_p20", Int16, agv_p20_callback, queue_size=1, buff_size=2**24) 
    
    rate = rospy.Rate(10) #1 vez a cada 50ms
    
    t2 = threading.Thread(target=Thread_logica)
    t2.start()
    
    #time.sleep(10)
  
    while not rospy.is_shutdown():
       
        rate.sleep()