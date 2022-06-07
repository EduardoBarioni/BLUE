#!/usr/bin/env python

import rospy
from std_msgs.msg import Int16
from std_msgs.msg import String
from std_msgs.msg import Bool
from std_msgs.msg import ByteMultiArray
import Database

#Constantes de tempo
TEMPO_APAGADO = 2
TEMPO_ENTRE_PISCADAS = 10

#print(Database.Dados_iluminacao())
#dados = Database.getAllItems("Status")

#Variaveis
vermelho = 0
verde = 0
azul = 0
tipo = "aceso"
tempo = 0

tag = False
virtual = False

externo = False

con_tempo = 0

#buzzOn = False

estadoAtual = "Iniciando"

#Publishers
pub_vermelho = rospy.Publisher("agv_p47", Int16, queue_size=10)  #Vermelho
pub_verde = rospy.Publisher("agv_p48", Int16, queue_size=10)     #Verde
pub_azul = rospy.Publisher("agv_p49", Int16, queue_size=10)      #Azul
#pub_buz = rospy.Publisher(Tradutor.buzina, Bool, queue_size=10)                 #Buzina -- TESTE

#Para oscilar
crescendo = [True, True, True]
valor_oscilando = [0, 0, 0]

estado_antigo = "Iniciando"
def estado_callback(data):
    global vermelho
    global verde
    global azul
    global tipo
    global tempo
    global estadoAtual, estado_antigo
    global crescendo, valor_oscilando
    estadoAtual = data.data
    if(estadoAtual != estado_antigo):
        dados = Database.getItem("Status", "Nome", data.data)[0]
        #print(data.data)
        vermelho = dados[2]
        verde = dados[3]
        azul = dados[4]
        tipo = dados[5]
        tempo = dados[6]
        crescendo = [True, True, True]
        valor_oscilando = [0, 0, 0]
    estado_antigo = estadoAtual
    
id_antigo = " "
def tag_virtual_callback(data):
    global id_antigo, tag, virtual
    if(data.data != id_antigo):
        id_antigo = data.data
        virtual = True
        tag = True

tag_antiga = "0"
def tag_callback(data):
    global tag, tag_antiga
    if(str(data.data) != tag_antiga and estadoAtual == "Rodando"):
        tag_antiga = str(data.data)
        tag = True
    else:
        tag_antiga = str(data.data)

def pisca_feedback_callback(data):
    global tag
    tag = data.data
        
#def buzz_callback(data):
#    global buzzOn
#    buzzOn = data.data

if __name__ == '__main__':
    rospy.init_node('Iluminacao', anonymous=False)
    rospy.Subscriber("estado", String, estado_callback)
    rospy.Subscriber("agv_tag", String, tag_callback)
    rospy.Subscriber("tag_virtual_atual", String, tag_virtual_callback)
    rospy.Subscriber("pisca_feedback", Bool, pisca_feedback_callback) 
    #rospy.Subscriber("buzina", Bool, buzz_callback)

    rate = rospy.Rate(10) #20Hz --> 1 vez a cada 50ms #10Hz --> 1 vez a cada 100 ms

    #Para piscar
    estadoPiscando = True
    piscar = 0
    estadoOn = False
    
    estadoPiscando_tag = True
    piscar_tag = 0
    estadoOn_tag = False

    
    vermelho_value = 0
    azul_value = 0
    verde_value = 0
    
    while(not rospy.is_shutdown()):
        con_tempo += 1#0.5 para rate 20
        if(tag == True):
            if(estadoPiscando_tag):
                if(piscar_tag >= 3):
                    con_tempo = 0
                    piscar_tag = 0
                    estadoPiscando_tag = False
                elif(con_tempo >= 2 and estadoOn_tag):
                    con_tempo = 0
                    estadoOn_tag = False
                    vermelho_value = 0
                    azul_value = 0
                    #pub_vermelho.publish(0)
                    #pub_azul.publish(0)
                    piscar_tag = piscar_tag + 1
                elif (con_tempo >= TEMPO_APAGADO and not estadoOn_tag):
                    estadoOn_tag = True
                    con_tempo = 0
                    if(virtual == True):
                        vermelho_value = 100
                    else:
                        vermelho_value = 0
                    azul_value = 100
                    #pub_vermelho.publish(0)
                    #pub_azul.publish(100)
                        
            else:
                tag = False
                virtual = False
                vermelho_value = 0
                azul_value = 0
                #pub_vermelho.publish(0)
                #pub_azul.publish(0)
                estadoPiscando_tag = True
                con_tempo = 0
        elif(not externo):
            if tipo == "aceso":
                vermelho_value = vermelho
                azul_value = azul
                verde_value = verde
                #pub_vermelho.publish(vermelho)
                #pub_azul.publish(azul)
            elif tipo == "oscilando":
                if (con_tempo >= (tempo/100)):
                    con_tempo = 0
                    if (crescendo[0] == True):
                        valor_oscilando[0] = valor_oscilando[0] + 1
                        if (valor_oscilando[0] >= vermelho):
                            crescendo[0] = False
                    else:
                        valor_oscilando[0] = valor_oscilando[0] - 1
                        if (valor_oscilando[0]== 0):
                            crescendo[0] = True
                    if (crescendo[1] == True):
                        valor_oscilando[1] = valor_oscilando[1] + 1
                        if (valor_oscilando[1] >= verde):
                            crescendo[1] = False
                    else:
                        valor_oscilando[1] = valor_oscilando[1] - 1
                        if (valor_oscilando[1]== 0):
                            crescendo[1] = True

                    if (crescendo[2] == True):
                        valor_oscilando[2] = valor_oscilando[2] + 1
                        if (valor_oscilando[2] >= azul):
                            crescendo[2] = False
                    else:
                        valor_oscilando[2] = valor_oscilando[2] - 1
                        if (valor_oscilando[2]== 0):
                            crescendo[2] = True
                    #print("Valor vermelho: " + str(valor_oscilando[0]))
                    #print("Valor verde: " + str(valor_oscilando[1]))
                    #print("Valor azul: " + str(valor_oscilando[2]))
                    if(vermelho == 0):
                        valor_oscilando[0] = 0
                    if(verde == 0):
                        valor_oscilando[1] = 0
                    if(azul == 0):
                        valor_oscilando[2] = 0
                    vermelho_value = valor_oscilando[0]
                    verde_value = valor_oscilando[1]
                    azul_value = valor_oscilando[2]
                    #pub_vermelho.publish(valor_oscilando[0])
                    #pub_azul.publish(valor_oscilando[2])
            else: #Pisca X vezes
                if(estadoPiscando):
                    if(piscar >= int(tipo)):
                        con_tempo = 0
                        piscar = 0
                        estadoPiscando = False
                    elif(con_tempo >= (tempo/100) and estadoOn):
                        con_tempo = 0
                        estadoOn = False
                        vermelho_value = 0
                        azul_value = 0
                        verde_value = 0
                        #pub_vermelho.publish(0)
                        #pub_azul.publish(0)
                        piscar = piscar + 1
                    elif (con_tempo >= TEMPO_APAGADO and not estadoOn):
                        estadoOn = True
                        con_tempo = 0
                        vermelho_value = vermelho
                        azul_value = azul
                        verde_value = verde
                        #pub_vermelho.publish(vermelho)
                        #pub_azul.publish(azul)     
                else:
                    vermelho_value = 0
                    azul_value = 0
                    verde_value = 0
                    #pub_vermelho.publish(0)
                    #pub_azul.publish(0)
                    if(con_tempo >= TEMPO_ENTRE_PISCADAS):
                        estadoPiscando = True
                        con_tempo = 0
        pub_vermelho.publish(vermelho_value)
        pub_azul.publish(azul_value)
        pub_verde.publish(verde_value)
        #pub_buz.publish(buzzOn)
        rate.sleep()
