#!/usr/bin/env python

import Database
import rospy
from std_msgs.msg import Bool
from std_msgs.msg import String
carregando = False
desacoplar = False
interlock = False

pub_enviar_msg_xbee = rospy.Publisher("enviar_msg_xbee", String, queue_size=10)

pub_agv_p12 = rospy.Publisher("agv_p12", Bool, queue_size=10)
pub_agv_p4 = rospy.Publisher("agv_p4", Bool, queue_size=10)
pub_carregador_debug = rospy.Publisher("carregador_debug", String, queue_size=10)

tag_atual = "0"

def carregador_callback(val):
    global carregando   
    carregando = val.data
    
def desacoplar_callback(val):
    global desacoplar, modo_carregador
    desacoplar = val.data
    if(desacoplar):
        modo_carregador = 1
        
anterior_interlock = False
def interlock_callback(val):
    global interlock, modo_carregador, anterior_interlock
    interlock = val.data
    
    if(interlock == True and anterior_interlock == False):
        modo_carregador = 3
    
    anterior_interlock = interlock
    
def tag_callback(data):
    global tag_atual
    tag_atual = str(data.data)

if __name__ == '__main__':
    rospy.init_node('Carregador', anonymous=False)
    rospy.Subscriber("carregar", Bool, carregador_callback)
    rospy.Subscriber("interlock", Bool, interlock_callback)
    rospy.Subscriber("desacoplar", Bool, desacoplar_callback)
    rospy.Subscriber("tag_atual", String, tag_callback)
    rate = rospy.Rate(1) # 1Hz --> 1 vez por segundo
    modo_carregador = 0
    count_rst = 0
    while not rospy.is_shutdown():
        if (carregando == True):
            if(modo_carregador == 0 and interlock == False): #Acoplar
                #tag = Database.getItem("RFID", "id", "1")[0][1]
                dadosCarregador = Database.getItem("Carregadores", "Tag", str(tag_atual))[0]
                msgEnviar = dadosCarregador[3]
                mac = dadosCarregador[0]
                pub_enviar_msg_xbee.publish(mac + "//" + msgEnviar)
                print("Enviando " + str(mac) + "//" + str(msgEnviar))
                pub_carregador_debug.publish("Enviando " + str(mac) + "//" + str(msgEnviar))
                count_rst += 1
                desacoplar = False
                pub_agv_p12.publish(True)
                pub_agv_p4.publish(True)
                
                #if(count_rst == 21):
                #    modo_carregador = 2             
            elif(modo_carregador == 1): #Desacoplar
                #tag = Database.getItem("RFID", "id", "1")[0][1]
                dadosCarregador = Database.getItem("Carregadores", "Tag", str(tag_atual))[0]
                msgEnviar = dadosCarregador[4]
                mac = dadosCarregador[0]
                pub_enviar_msg_xbee.publish(mac + "//" + msgEnviar)
                print("Enviando " + str(mac) + "//" + str(msgEnviar))
                pub_carregador_debug.publish("Enviando " + str(mac) + "//" + str(msgEnviar))
                count_rst = 0
                
                pub_agv_p12.publish(True)
                pub_agv_p4.publish(True)
                if(interlock == False):
                    pub_agv_p12.publish(True)
                    pub_agv_p4.publish(True)
                
            elif(modo_carregador == 2 and interlock == False): #Resetar
                #tag = Database.getItem("RFID", "id", "1")[0][1]
                dadosCarregador = Database.getItem("Carregadores", "Tag", str(tag_atual))[0]
                msgEnviar = dadosCarregador[5]
                mac = dadosCarregador[0]
                pub_enviar_msg_xbee.publish(mac + "//" + msgEnviar)
                print("Enviando " + str(mac) + "//" + str(msgEnviar))
                pub_carregador_debug.publish("Enviando " + str(mac) + "//" + str(msgEnviar))
                desacoplar = False
                count_rst = 0
                pub_agv_p12.publish(True)
                pub_agv_p4.publish(True)
                
            elif(modo_carregador == 3 and interlock == True): #Envia conectado
                dadosCarregador = Database.getItem("Carregadores", "Tag", str(tag_atual))[0]
                msgEnviar = dadosCarregador[6]
                mac = dadosCarregador[0]
                pub_enviar_msg_xbee.publish(mac + "//" + msgEnviar)
                print("Enviando " + str(mac) + "//" + str(msgEnviar))
                pub_carregador_debug.publish("Enviando " + str(mac) + "//" + str(msgEnviar))
                count_rst = 0    
                pub_agv_p12.publish(False)
                pub_agv_p4.publish(True)
                
            else:
                pub_agv_p12.publish(True)
                pub_agv_p4.publish(True)
                desacoplar = False
                count_rst = 0
        else:
            pub_agv_p12.publish(False)
            pub_agv_p4.publish(False)
            modo_carregador = 0
            count_rst = 0
        rate.sleep()