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
pub_debug_G1EA1800CV1 = rospy.Publisher("pub_debug_G1EA1800CV1", String, queue_size=10, tcp_nodelay=True) #Debug Serial

altura_set = 10
posicionar = False

pub_Freio = rospy.Publisher("agv_p9", Bool, queue_size=10, tcp_nodelay=True)
pub_Frente = rospy.Publisher("agv_p5", Bool, queue_size=10, tcp_nodelay=True)
pub_Re = rospy.Publisher("agv_p6", Bool, queue_size=10, tcp_nodelay=True)
pub_hab_locomocao = rospy.Publisher("agv_p14", Bool, queue_size=10, tcp_nodelay=True)
pub_seg_acelerador = rospy.Publisher("agv_p7", Bool, queue_size=10, tcp_nodelay=True)
pub_acelerador = rospy.Publisher("agv_p45", Int16, queue_size=10, tcp_nodelay=True)                            #Direcao
pub_alavanca = rospy.Publisher("agv_p46", Int16, queue_size=10, tcp_nodelay=True)                            #Direcao
pub_volante = rospy.Publisher("agv_volante", Int16, queue_size=10, tcp_nodelay=True) 



pwm = 45
velocidade = 0
andar = False
logicaAcionarmento = 0
volante = 0


reset_acelerador = 0

def Thread_logica():
    global altura_set, posicionar, ok, altura_Atual, pwm, velocidade, andar, logicaAcionarmento, volante, reset_acelerador

    while not rospy.is_shutdown():
        try:
            print("velocidade: " + str(velocidade) + " logicaAcionarmento: " + str(logicaAcionarmento) + " Volante: " + str(volante))
            if( (velocidade > 0 or velocidade < 0)):
                reset_acelerador = 0;
                pub_Freio.publish(True)
                logicaAcionarmento = logicaAcionarmento+1
                if (logicaAcionarmento < 20):
                    pub_volante.publish(0)
                    pub_hab_locomocao.publish(False)
                    pub_Frente.publish(False)
                    pub_Re.publish(False)
                    pub_acelerador.publish(0)
                    pub_alavanca.publish(45)
                    pub_seg_acelerador.publish(False)
                elif (logicaAcionarmento < 40):
                    pub_volante.publish(0)
                    pub_hab_locomocao.publish(True)
                    pub_Frente.publish(False)
                    pub_Re.publish(False)
                    pub_acelerador.publish(0)
                    pub_alavanca.publish(45)
                    pub_seg_acelerador.publish(False)
                elif (logicaAcionarmento < 50):
                    pub_volante.publish(0)
                    pub_hab_locomocao.publish(True)
                    pub_seg_acelerador.publish(False)
                    pub_acelerador.publish(0)
                    if(velocidade > 0):
                        pub_Frente.publish(True)
                        pub_Re.publish(False)
                    else:
                        pub_Frente.publish(False)
                        pub_Re.publish(True)
                    pub_alavanca.publish(45)    
                else:
                    pub_volante.publish(volante)
                    pub_hab_locomocao.publish(True)
                    pub_seg_acelerador.publish(True)
                    if(velocidade > 0):
                        pub_Frente.publish(True)
                        pub_Re.publish(False)
                        pub_alavanca.publish(int(pwm))
                        pub_acelerador.publish(velocidade)
                    else:
                        pub_Frente.publish(False)
                        pub_Re.publish(True)
                        pub_alavanca.publish(int(pwm))
                        pub_acelerador.publish(velocidade*-1)


                
            else:
                reset_acelerador = reset_acelerador + 1
                pub_seg_acelerador.publish(False)
                pub_Freio.publish(False)
                pub_Re.publish(False)
                pub_Frente.publish(False)
                logicaAcionarmento = 0
                if(pwm != 45 or volante != 0 or reset_acelerador > 1000):
                    pub_hab_locomocao.publish(True)
                    pub_acelerador.publish(80)
                else:
                    pub_hab_locomocao.publish(False)
                    pub_acelerador.publish(0)
                if(reset_acelerador > 1010):
                    reset_acelerador = 0
                
                pub_alavanca.publish(int(pwm))
                pub_debug_G1EA1800CV1.publish("pwm: " + str(pwm))
                pub_volante.publish(volante)
            time.sleep(0.05)
                
        except Exception as ex:
            print ("Erro __main__ G1EA1800CV1: " + str(ex))
            #pub_ros_debug.publish("Erro __main__ G1EA1800CV1: " + str(ex))
            
def G1EA1800CV1_volante_callback(data):
    global volante
    volante = data.data
     
def G1EA1800CV1_garfo_acionar_callback(data):
    global pwm
    pwm = data.data

def G1EA1800CV1_velocidade_callback(data):
    global velocidade
    velocidade = data.data
    andar = True

            
if __name__ == '__main__':
    rospy.init_node('G1EA1800CV1', anonymous=False)
    
    rospy.Subscriber("G1EA1800CV1_garfo_acionar", Int16, G1EA1800CV1_garfo_acionar_callback, queue_size=1, buff_size=2*24)
    rospy.Subscriber("G1EA1800CV1_velocidade", Int16, G1EA1800CV1_velocidade_callback, queue_size=1, buff_size=2*24)
    rospy.Subscriber("G1EA1800CV1_volante", Int16, G1EA1800CV1_volante_callback, queue_size=1, buff_size=2*24)
    
    rate = rospy.Rate(10) #1 vez a cada 50ms
    
    t2 = threading.Thread(target=Thread_logica)
    t2.start()
    
    #time.sleep(10)
  
    while not rospy.is_shutdown():
       
        rate.sleep()