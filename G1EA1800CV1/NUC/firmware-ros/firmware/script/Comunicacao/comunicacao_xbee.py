#!/usr/bin/env python


#########################33
#
#
#
############################



from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
import serial
import time
import rospy
from std_msgs.msg import Bool
from std_msgs.msg import String
from std_msgs.msg import Int16
from std_msgs.msg import Float32
from std_msgs.msg import Float64
from std_msgs.msg import ByteMultiArray 
import json
import numpy
import sqlite3
import rospkg
import interface_bd as interface_bd

PORT = "/dev/ttyXbee"
BAUD_RATE = 115200
device = XBeeDevice(PORT, BAUD_RATE)
remote_mac = "0013A200419DA006" #"0013A2004190523F"
Status = 36
#Dados do banco
caminho = "";
bd_nome = "/AGVConfig.db";
pkg_nome = "banco_pk_zf"

#Variaveis globais
topico_tag_atual = "tag_atual"
topico_bateria = "/bateria"
valor_bateria = 0
topico_velocidade = "/agv_encoder"
valor_velocidade = 0

topico_status = "/estado"
valor_status= "Rodando"

topico_acao = "/acao"

topico_enviar_msg = "/enviar_msg_xbee"
topico_erro = "/erro_firmware"


ControleMSG_atual = ""
valor_tag_atual = 0
conectado = 0
config_agv = []
porta_liberada = 0

rota_atual = 0
AGVS_disponivel = 1
carregando = 0



debug = 0

CMDS = [0,0,0,0]

Tags_CMDS = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
Tags_CMDS_becape = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

#
rota_inicial = 0
rota_inicial_antiga = 0

pub_ros_debug = rospy.Publisher("ros_debug_xbee", String, queue_size=10)

pub_sinal_msg = rospy.Publisher("sinal_mensagem", String, queue_size=10)



#Desenvolvedor: Marco 
#Explicação: Função utilizada para enviar uma resposta ao supervisório, com os status do rebocador. 
#Condição: É chamada sempre que o rebocador recebe um comando do supervisório do tipo 0xa ou 0xff. 
def enviar_resposta():
    try:
        debug_local = 0
        if debug == 1 or debug_local==1:
                print("Estou no envia resposta")
        #print("Enviando resposta")
        verifica_disponibilidade_pega_rota()
        pega_status()
        data = [0]*30
        data[0] = 0x35
        data[1] = config_agv["idAGV"] #Numero do AGV
        #Conversao
        try:
                valor = int(valor_tag_atual)
        except:
                valor = 0        
        #valor = 2
        if valor != 0:
                data[2] = (valor - int(valor/256)*256)&0xff #TAG
                data[3] = int(valor/256)             #TAG
        else: 
                data[2] = 0 #TAG
                data[3] = 0  #TAG

        #        #---------------------------
        #data[4] = Status #estatus atual _ segundo tabela
        if debug ==1:
         print("Estatus atual é: "+str(status))

        try:
                data[4] = status
        except:
                data[4] = 37      
         

        #        #Velocidade 
        #valor = int(valor_velocidade)
        valor = int(valor_velocidade*10)
        if valor!= 0: 
                data[5] = (valor - int(valor/256)*256)&0xff #TAG
                data[6] = int(valor/256)             #TAG
        else:
                data[5] = 0#TAG
                data[6] = 0           #TAG        
        #        #############
        #Se todas as tabelas de rotas estiverem que nem a inicial
        #Quando estiver disponivel retorna 0
        #Quando estiver não disponivel retorna 1   

        data[7] = AGVS_disponivel #AGV disponivel - Quando o vetor estiver que nem a rota inicial 
        data[8] =  int(rota_atual) #Rota atual
        # data[9:20] = 0 #Nada por hora 
        data[21] = 0#Modo chuva
        data[22] = 1#Controle encoder
        #       
        #Bateria - depois
        valor = round(valor_bateria)
        if valor != 0:
                
                data[23] = (valor - int(valor/256)*256)&0xff #TAG
                data[24] = int(valor/256)             #TAG
        else:
                data[23] = 0#TAG
                data[24] = 0   #TAG        

        ##Pegar a informação logica da placa, inter- porta29
        data[25] = carregando #carregando
        data[26] = 1 #agv parar bateria baixa 
        valor = 0
        data[27] = (valor - int(valor/256)*256)&0xff 
        data[28] = int(valor/256)             

        soma = 0     
        for i in range(0,len(data)-1):
             soma = soma+data[i]
                      
        data[29] = soma&0xff#


        if porta_liberada == 1:
                       if debug == 1 or debug_local==1:
                                print("Enviando msg")
                       remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(remote_mac))
                       device.send_data_async(remote_device,bytes(data))    
                       if debug == 1 or debug_local==1:
                                print("msg enviada")
    except Exception as ex:
        pub_ros_debug.publish("ERRO enviar_resposta: " + str(ex)) 


                                              

def inicia_comunicacao():
        global device
        global porta_liberada
        try:
                #Muda estatus do xbee
                ser = serial.Serial(PORT, 9600) 
                for i in range(3):
                    ser.write(b'\n\n')
                    time.sleep(0.5)
                    ser.write(b'B')
                    time.sleep(0.5)
                    ser.write(b'\n\n')
                ser.close() 
                
                #Cria comunicacao
                device = XBeeDevice(PORT, BAUD_RATE)
                device.open()
                time.sleep(1)
                porta_liberada = 1
                print("Comunicacao iniciada")
        except Exception as ex:
                time.sleep(5)
                #if debug ==1:
                print("Erro na comunicacao: " + str(ex))
                inicia_comunicacao()
 
 
def envia_acao(data):
#        print("Entrei no envia acao")
        if primeira_vez_acao != 0:
                pub_acao.publish(data)
        
        
#Se tudo zero, reseta o sistema
#O byte vai incrementando
#Byte 1 = Play
#Byte 2 = Stop cruzamento
#Byte 3 = Stop automatico
#Byte 4 = Emergencia remoto
primeira_vez_acao = 0
def data_receive_callback(xbee_message):
    try:
        #time.sleep(3)
        global remote_mac 
        global conectado
        global CMDS
        global primeira_vez_acao
        global rota_inicial
        global rota_inicial_antiga
        global carregadores_mac
        r_m = str(xbee_message.remote_device.get_64bit_addr())

        #print("Dados recebidos!")
        if debug == 1:
            print("----------")
            print("MSG recebida: "+str(xbee_message.data) + " do MAC " + str(r_m))
            #print("Primeiro byte: " + str(xbee_message.data[0]) + " com tamanho: " + str(len(xbee_message.data)))

        #Sinais provenientes dos painéis
        #Mensagens de quase-pronto, pronto e erro
        #if(str(xbee_message.data) == "?"):
        #    pub_sinal_msg.publish("msg")

        try:
            interface_bd.conecta_bd()
            carregadores = interface_bd.getCarregadores()
            #print("Tag atual = " + str(valor_tag_atual))
            #teste = interface_bd.getCarregadorFromTag(str(valor_tag_atual))
            #print(teste)
            msg_liberar = interface_bd.getCarregadorFromTag(str(valor_tag_atual))[0][7]
            #print("Msg_liberar = " + str(msg_liberar))
            #print("Valor tag atual: " + str(valor_tag_atual))
            carregadores_mac = [item[0] for item in carregadores] 
            #print("Carregadores_mac = " + str(carregadores_mac))
            if(r_m in carregadores_mac):
                print("Mensagem de carregador! A mensagem de liberar desse carregador: " + str(msg_liberar))
                #do carregador stuffs
                if (str(msg_liberar) == xbee_message.data.decode()):
                    #Liberar AGV - Sair do carregador
                    pub_fim_carregador.publish(True)
                    #pass 
                else:
                    print("Msg recebida do carregador: " + str(xbee_message.data.decode()))
                return
        except Exception as ex:
            #print("Erro carregador: " + str(ex))
            #Nao ha carregador nessa tag
            pass
              
        remote_mac = str(xbee_message.remote_device.get_64bit_addr())    
        if (hex(xbee_message.data[0]) ==  hex(0xff)) and len(xbee_message.data)>37 :
            #print("Recebeu mensagem que comeca com 0xff")
            soma = 0     
            for i in range(0,len(xbee_message.data)-1):
                    soma = soma+xbee_message.data[i]
            soma = soma&0xff      
            if (soma == xbee_message.data[37]):  
                    
                    if  CMDS[0] != xbee_message.data[1]:
                            CMDS[0] = xbee_message.data[1]
                            if(valor_status != "Carregando"):
                                envia_acao(1)
                            #print("Recebeu do supervisorio que é para sair")
                    if  CMDS[1] != xbee_message.data[2]:
                            CMDS[1] = xbee_message.data[2]  
                            envia_acao(37)
                    if  CMDS[2] != xbee_message.data[3]:
                            CMDS[2] = xbee_message.data[3]
                            envia_acao(2)
                    if  CMDS[3] != xbee_message.data[4]:
                            CMDS[3] = xbee_message.data[4]      
                            envia_acao(38)    
                    
                    primeira_vez_acao = 1
                    
                    #Tags virtuais
                    Tags_CMDS[0] = (xbee_message.data[6]*256+xbee_message.data[5]) #Tag1 - Cruzamento - se receber e ler essa tag, tem que parar o agv por cruzamento  
                    Tags_CMDS[1] = (xbee_message.data[8]*256+xbee_message.data[7]) #Tag2 - Cruzamento  
                    Tags_CMDS[2] = (xbee_message.data[10]*256+xbee_message.data[9])    
                    Tags_CMDS[3] = (xbee_message.data[12]*256+xbee_message.data[11])    
                    Tags_CMDS[4] = (xbee_message.data[14]*256+xbee_message.data[13]) 
                    Tags_CMDS[5] = (xbee_message.data[16]*256+xbee_message.data[15]) 
                    Tags_CMDS[6] = (xbee_message.data[18]*256+xbee_message.data[17]) 
                    Tags_CMDS[7] = (xbee_message.data[20]*256+xbee_message.data[19]) 
                    Tags_CMDS[8] = (xbee_message.data[22]*256+xbee_message.data[21]) 
                    Tags_CMDS[9] = (xbee_message.data[24]*256+xbee_message.data[23]) 
                    Tags_CMDS[10] = (xbee_message.data[26]*256+xbee_message.data[25]) 
                    Tags_CMDS[11] = (xbee_message.data[28]*256+xbee_message.data[27]) 
                    Tags_CMDS[12] = (xbee_message.data[30]*256+xbee_message.data[29]) 
                    Tags_CMDS[13] = (xbee_message.data[32]*256+xbee_message.data[31]) 
                    #Tags_CMDS[14] = (xbee_message.data[34]*256+xbee_message.data[33]) 
                   
                    add_Tags_CMDS()
                    

                    if rota_inicial != xbee_message.data[34]:
                            rota_inicial_antiga = rota_inicial
                            rota_inicial = xbee_message.data[34]
                            print("Entrei no modifica ROTA com mensagem vindo do " + str(remote_mac))
                            modificar_rota_inicial()
                            
                    enviar_resposta();
            else:
                    print("Soma diferente")
              
        elif (hex(xbee_message.data[0]) ==  hex(0xfd)) and len(xbee_message.data)>10:
            if debug ==1:
                print("----------")
                print("Entrei no rota")
            
            Rotas_temp = [rota_inicial]*10
            
            #print((xbee_message.data[0]))
            #print((xbee_message.data[1]))
            #print((xbee_message.data[2]))
            #print((xbee_message.data[3]))
            #print((xbee_message.data[4]))
            #print((xbee_message.data[5])) 
            #print((xbee_message.data[6])) 
            #print((xbee_message.data[7]))
            #print((xbee_message.data[8]))
            #print((xbee_message.data[9]))
            #print((xbee_message.data[10])) 
            
            for i in range(1, len(xbee_message.data)):
                #print((xbee_message.data[i]))
                if(xbee_message.data[i] != 0):
                    Rotas_temp[i-1] = xbee_message.data[i]
            #print(Rotas_temp)
            interface_bd.conecta_bd()
            interface_bd.add_rotas(1,Rotas_temp[0],Rotas_temp[1], Rotas_temp[2],Rotas_temp[3],Rotas_temp[4], Rotas_temp[5], Rotas_temp[6],Rotas_temp[7], Rotas_temp[8], Rotas_temp[9])             
                            
            if(valor_status != "Rodando" and Rotas_temp[0] != rota_inicial):
                envia_acao(1)
                #with open('log_supervisorio', 'a') as f:
                #    f.write("Recebeu rota: " + str(Rotas_temp[0]) + ", " + str(Rotas_temp[1]) + ", " + str(Rotas_temp[2]) + " ... \n")
            #print(xbee_message.data[6]*256+xbee_message.data[5])   
            #print(xbee_message.data[7:8]) Tag2 - Cruzamento  
            #print(xbee_message.data[9:10]) Tag3 - Cruzamento        
            #print(xbee_message.data[11:12]) Tag4 - Cruzamento     

            
        elif (hex(xbee_message.data[0]) ==  hex(0xa)) and len(xbee_message.data)>37:
            #print("Recebeu mensagem que comeca com 0xa")
            soma = 0     
            for i in range(0,len(xbee_message.data)-1):
                    soma = soma+xbee_message.data[i]
            soma = soma&0xff      
            if (soma == xbee_message.data[37]):  
                    if  CMDS[0] != xbee_message.data[1]:
                            CMDS[0] = xbee_message.data[1]
                            if(valor_status != "Carregando"):
                                envia_acao(1)
                            #print("Recebeu do supervisorio que deve sair 2")
                    if  CMDS[1] != xbee_message.data[2]:
                            CMDS[1] = xbee_message.data[2]  
                            envia_acao(37)
                    if  CMDS[2] != xbee_message.data[3]:
                            CMDS[2] = xbee_message.data[3]
                            envia_acao(2)
                    if  CMDS[3] != xbee_message.data[4]:
                            CMDS[3] = xbee_message.data[4]      
                            envia_acao(38)    
                    
                    primeira_vez_acao = 1
                    
                    #Tags virutais
                    Tags_CMDS[0] = (xbee_message.data[6]*256+xbee_message.data[5]) #Tag1 - Cruzamento - se receber e ler essa tag, tem que parar o agv por cruzamento  
                    Tags_CMDS[1] = (xbee_message.data[8]*256+xbee_message.data[7]) #Tag2 - Cruzamento  
                    Tags_CMDS[2] = (xbee_message.data[10]*256+xbee_message.data[9])    
                    Tags_CMDS[3] = (xbee_message.data[12]*256+xbee_message.data[11])    
                    Tags_CMDS[4] = (xbee_message.data[14]*256+xbee_message.data[13]) 
                    Tags_CMDS[5] = (xbee_message.data[16]*256+xbee_message.data[15]) 
                    Tags_CMDS[6] = (xbee_message.data[18]*256+xbee_message.data[17]) 
                    Tags_CMDS[7] = (xbee_message.data[20]*256+xbee_message.data[19]) 
                    Tags_CMDS[8] = (xbee_message.data[22]*256+xbee_message.data[21]) 
                    Tags_CMDS[9] = (xbee_message.data[24]*256+xbee_message.data[23]) 
                    Tags_CMDS[10] = (xbee_message.data[26]*256+xbee_message.data[25]) 
                    Tags_CMDS[11] = (xbee_message.data[28]*256+xbee_message.data[27]) 
                    Tags_CMDS[12] = (xbee_message.data[30]*256+xbee_message.data[29]) 
                    Tags_CMDS[13] = (xbee_message.data[32]*256+xbee_message.data[31]) 
                    Tags_CMDS[14] = (xbee_message.data[34]*256+xbee_message.data[33]) 
                    Tags_CMDS[15] = (xbee_message.data[36]*256+xbee_message.data[35])
                    
                    add_Tags_CMDS()

                    
                    enviar_resposta();
            else:
                    print("Soma diferente")

        else:
            if debug ==1:
                    print("A msg não está no padrão!")
            #print(xbee_message.data.decode())
            verifica_acao(xbee_message.data.decode())
            
    except Exception as ex:
        pub_ros_debug.publish("ERRO data_receive_callback: " + str(ex))      

                
def verifica_acao(data):
    global ControleMSG_atual
#       print(data)
    try:
        #control_msg
        Rotas_temp = []

        if (ControleMSG_atual != data):
                ControleMSG_atual = data
                for i in range(0, len(ControleMSG)):
                        if (ControleMSG[i]["MSG"] == ControleMSG_atual):
                            Rotas_temp =  ControleMSG[i]
                            break
                if Rotas_temp == []:
#                        print("Não existe este comando no banco de dados")
                        return                        
                else:
#                        print("Valor de tag"+str(Rotas_temp["Tag"]))
                        if   str(Rotas_temp["Tag"])  ==  str(valor_tag_atual):
                                print("Recebimento de rota: " + str(data))
                                interface_bd.conecta_bd()
                                interface_bd.add_rotas(1,Rotas_temp["Rota1"],Rotas_temp["Rota2"], Rotas_temp["Rota3"],Rotas_temp["Rota4"],Rotas_temp["Rota5"], Rotas_temp["Rota6"], Rotas_temp["Rota7"],Rotas_temp["Rota8"], Rotas_temp["Rota9"], Rotas_temp["Rota10"])             
                                pub_acao.publish(1)
                                print("Publicando acao")
#                print("Eu recebi uma msg diferente da que tinha recebido antes!")
    except Exception as e:
        pub_ros_debug.publish("ERRO Verifica_acao: " + str(e))

    
def add_Tags_CMDS():
        interface_bd.conecta_bd()
        try:
                if (Tags_CMDS_becape[0] != Tags_CMDS[0]):
                        interface_bd.add_Tags_CMDS(1,Tags_CMDS[0])
                if Tags_CMDS_becape[1] != Tags_CMDS[1]:        
                        interface_bd.add_Tags_CMDS(2,Tags_CMDS[1])
                if Tags_CMDS_becape[2] != Tags_CMDS[2]:        
                        interface_bd.add_Tags_CMDS(3,Tags_CMDS[2])
                if Tags_CMDS_becape[3] != Tags_CMDS[3]:        
                        interface_bd.add_Tags_CMDS(4,Tags_CMDS[3])
                if Tags_CMDS_becape[4] != Tags_CMDS[4]:        
                        interface_bd.add_Tags_CMDS(5,Tags_CMDS[4])
                if Tags_CMDS_becape[5] != Tags_CMDS[5]:        
                        interface_bd.add_Tags_CMDS(6,Tags_CMDS[5])
                if Tags_CMDS_becape[6] != Tags_CMDS[6]:        
                        interface_bd.add_Tags_CMDS(7,Tags_CMDS[6])
                if Tags_CMDS_becape[7] != Tags_CMDS[7]:        
                        interface_bd.add_Tags_CMDS(8,Tags_CMDS[7])
                if Tags_CMDS_becape[8] != Tags_CMDS[8]:
                        interface_bd.add_Tags_CMDS(9,Tags_CMDS[8])
                if Tags_CMDS_becape[9] != Tags_CMDS[9]:
                        interface_bd.add_Tags_CMDS(10,Tags_CMDS[9])
                if Tags_CMDS_becape[10] != Tags_CMDS[10]:
                        interface_bd.add_Tags_CMDS(11,Tags_CMDS[10])
                if Tags_CMDS_becape[11] != Tags_CMDS[11]:
                        interface_bd.add_Tags_CMDS(12,Tags_CMDS[11])
                if Tags_CMDS_becape[12] != Tags_CMDS[12]:
                        interface_bd.add_Tags_CMDS(13,Tags_CMDS[12])
                if Tags_CMDS_becape[13] != Tags_CMDS[13]:
                        interface_bd.add_Tags_CMDS(14,Tags_CMDS[13])
                if Tags_CMDS_becape[14] != Tags_CMDS[14]:
                        interface_bd.add_Tags_CMDS(15,Tags_CMDS[14])
                if Tags_CMDS_becape[15] != Tags_CMDS[15]:
                        interface_bd.add_Tags_CMDS(16,Tags_CMDS[15])
                Tags_CMDS_becape[:] = Tags_CMDS[:]
        except:
                print("Erro no add Tags CMDS")
                
                
def fecha_comunicacao():
        global porta_liberada
           
        if device is not None and device.is_open():
                        device.close() 
        porta_liberada = 0

      

def callback_tag_atual(data):
        global valor_tag_atual
        valor_tag_atual = data.data
        if debug ==1: 
                print("Valor tag atual: "+str(valor_tag_atual))

             
def callback_bateria(data):
        global valor_bateria
        valor_bateria = data.data 
       
        
def callback_velocidade(data):
        global valor_velocidade
        valor_velocidade = (data.data*3.6)     
        
             
def verifica_disponibilidade_pega_rota():
        global AGVS_disponivel
        global rota_atual
        interface_bd.conecta_bd()
        temp = interface_bd.get_rota()[0]
        rota_atual = temp["Rota1"]
        
        for i in range(0, 10):
                temp2 = "Rota"+str(i+1)
                if temp[temp2] != config_agv["RotaInicial"]:
                        AGVS_disponivel = 1
                        break
                AGVS_disponivel = 0       
        #print("AGV disponivel"+str(AGVS_disponivel))
      
                   
def pega_status():
        global status
        interface_bd.conecta_bd()
        if debug ==1:
                print ("valor_status  "+str(valor_status))
        status = interface_bd.get_status(valor_status)
        #print(status)

def callback_status(data):
        global valor_status
        valor_status = data.data
        
def p28_callback(data):
        global carregando
        carregando = 1 - (int(data.data))     
        
def modificar_rota_inicial():
    try:
#        print("-------------------------------------------")
#        print("Valor de rota inicial nova: "+str(rota_inicial))
#        print("Valor de rota inicial antiga: "+str(rota_inicial_antiga))
        interface_bd.conecta_bd()
        temp = interface_bd.get_rota()
        for i in range(1,11):
                temp2 = "Rota"+str(i)
                
                if temp[0][temp2] == rota_inicial_antiga:
                        temp[0][temp2] = rota_inicial
                        print("Opa!! "+str(temp[0][temp2]))
                    
#        print("Estou colocando a rota")    
        interface_bd.add_rotas(1,temp[0]["Rota1"],temp[0]["Rota2"], temp[0]["Rota3"],temp[0]["Rota4"],temp[0]["Rota5"], temp[0]["Rota6"], temp[0]["Rota7"],temp[0]["Rota8"], temp[0]["Rota9"], temp[0]["Rota10"])  
        interface_bd.set_nova_rota_inicial(int(config_agv["idAGV"]),rota_inicial)    
#        print("Estou saindo da rota")
    except Exception as ex:
        pub_ros_debug.publish("ERRO modificar_rota_inicial: " + str(ex)) 

    
#Ola  

def callback_enviar_msg(data):
        global device
        try:
                msg = data.data.split('//') 
                #remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(remote_mac))
                #device.send_data_async(msg[0],msg[1])
                #print("MAC carregador: " + str(msg[0]))
                pub_ros_debug.publish("enviando MAC carregador: " + str(msg[0]))
                r_d = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(msg[0]))
                device.send_data_async(r_d,msg[1])                
        except Exception as ex:
                print("Erro ao enviar mensagem: " + str(ex))
                pub_erro.publish("Erro no comunicao - callback_enviar_msg - tentando enviar a msg: "+str(data.data))
                         

          
if __name__ == '__main__':
        rospy.init_node('comunicacao_xbee')
             
        #Subscribe     
        rospy.Subscriber(topico_tag_atual, String, callback_tag_atual)
        rospy.Subscriber(topico_status, String, callback_status)
        rospy.Subscriber(topico_bateria, Float64, callback_bateria)
        rospy.Subscriber(topico_velocidade, Float32, callback_velocidade)
        rospy.Subscriber("agv_p28", Bool, p28_callback)
        rospy.Subscriber(topico_enviar_msg, String, callback_enviar_msg)

        
        #Publica
        pub_acao = rospy.Publisher(topico_acao, Int16, queue_size=10)
        pub_erro = rospy.Publisher(topico_erro, String, queue_size=10)
        pub_fim_carregador = rospy.Publisher("fim_carregar", Bool, queue_size = 10)
        
        rate = rospy.Rate(0.2) # 0.2Hz
        
        #xbeee comunicacao
        inicia_comunicacao()
        time.sleep(3)
        device.add_data_received_callback(data_receive_callback)
        
        #Inicia variaveis globais com BD
        interface_bd.conecta_bd()
        ControleMSG = interface_bd.get_all_ControlMSG()
        config_agv = interface_bd.get_configuracoes_agv()[0]
        rota_inicial = config_agv["RotaInicial"]
        rota_inicial_antiga =  config_agv["RotaInicial"]

        controle = interface_bd.getControl()
        tags_control = [item[1] for item in controle]
        #print(tags_control)
        con_msg_painel = 0
        
        while not rospy.is_shutdown():
            # if((str(valor_tag_atual) in tags_control) and (str(valor_status) != "Cadastro Tag")):
                # interface_bd.conecta_bd()
                # dado = interface_bd.getControlFromTag(str(valor_tag_atual))
                # mac_painel = dado[0][0]
                # print("Painel: " + str(mac_painel))
                # r_d = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(mac_painel))
                # msg_painel = dado[0][2]
                # device.send_data_async(r_d, msg_painel)
                
            
            rate.sleep()  
###             
        fecha_comunicacao()
                 

