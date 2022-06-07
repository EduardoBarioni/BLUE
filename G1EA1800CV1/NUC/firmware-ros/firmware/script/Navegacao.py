#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseWithCovarianceStamped, Pose
from geometry_msgs.msg import PointStamped, Vector3
from std_msgs.msg import String, ColorRGBA
from std_msgs.msg import Bool
from std_msgs.msg import Int16
from std_msgs.msg import Float32
from sensor_msgs.msg import LaserScan
import tf
from tf.transformations import euler_from_quaternion
import math
import Database
import time
import numpy as np
from visualization_msgs.msg import Marker
import cv2
import statistics


estadoAtual = "Iniciando" #Estado inicial
rotaAtual = Database.getAllItems("Configuracao")[0][1]

pos_x = 0   #Posição em X do AGV dada pelo HectorSlam; Considerando a posição inicial, X aumenta para "frente"
pos_y = 0   #Posição em Y do AGV dada pelo HectorSlam; Considerando a posição inicial, Y aumenta para a "esquerda"
roll = 0    #Ângulo em roll (não utilizado)
pitch = 0   #Ângulo em pitch (não utilizado)
yaw = 0     #Ângulo em yaw
yaw_graus = 0   #Ângulo em yaw convertido para graus

obj_x = 0           #Posição objetivo X
obj_y = 0           #Posição objetivo Y
distancia_obj = 0   #Distância linear do objetivo
angulo_obj = 0      #Ângulo do objetivo

sentido = 1


id_atual = -1       #Posição atual em relação aos pontos
id_prox = None      #Próxima posição
id_count = 0        
id_function = 0

fim_curso = True            #Indica se o garfo está no fim de curso
delay_garfo = 0             #Para não sair direto

#Scanner sendo usado para navegação e para zerar erro
# 0 = Scanner Frontal
# 1 = Scanner Traseiro
scanner_atual = 0
delay_troca_scanner = 30

reduz_vel = False #Redução de velocidade por scanner

limite_direcao_superior = 960#1023
limite_direcao_inferior = 252#310

rampa_aceleracao = 1

quase_coleta = False
pronto_coleta = False
quase_entrega = False
pronto_entrega = False
parada_coleta = False
parada_entrega = False
enable_parada_coleta = False
enable_parada_entrega = False

con_erro_plataforma = 0
LIM_ERRO_PLATAFORMA = 100 #5 segundos

andando = False
espera_garfo = False


margem = 0.15       #Margem de erro para encontrar pontos

offset_x = 0        #Valor a ser adicionado ao pos_x para corrigir posicionamento depois de zerar erro
offset_y = 0        #Valor a ser adicionado ao pos_y para corrigir posicionamento depois de zerar erro
offset_yaw = 0      #Valor a ser adicionado ao yaw_graus para corrigir posicionamento depois de zerar erro

#Para funções ----------------------------------------------------------
funcao = '0'       #Funções para serem executadas ao chegar no ponto

snap_x = 0          #Offset temporário
snap_y = 0          #Offset temporário
snap_yaw = 0        #Offset temporário

passo_funcao = 0    #Em qual parte da função está
con_funcao = 0      #Para dar delay entre as partes da função


#-----------------------------------------------------------------------

#Centro direção é baseado no valor do encoder de direção
try:
    CENTRO_DIRECAO = Database.getItem("ConfigPaleteira", "Item", "CENTRO_DIRECAO")[0][1]    #Valor do centro da direção
    print("Centro direção: " + str(CENTRO_DIRECAO))
except:
    CENTRO_DIRECAO = 695    #Como base, usa 153 --> Valor indicado pelo sensor de centro
    print("Centro direcao nao encontrado no BD")

try:
    DELAY_ENTRE_ACOES = (Database.getItem("ConfigPaleteira", "Item", "DELAY_ENTRE_ACOES")[0][1]) * 2 #Valor para delay entre ações (*2 porque é 20Hz)
    DELAY_ENTRE_ACOES = DELAY_ENTRE_ACOES /100
except:
    DELAY_ENTRE_ACOES = 24
    print("Delay entre acoes nao encontrado no BD")

try:
    vel_id = Database.getAllItems("Configuracao")[0][5]
    velocidade = Database.getItem("Velocidades", "ID", str(vel_id))[0][1]
    print("Velocidade inicial = " + str(velocidade))
except:
    velocidade = 10
    print("Velocidade inicial não encontrada no BD: 60 como padrão")



#----- PUBLISHERS ------#


pub_acelerador = rospy.Publisher("G1EA1800CV1_velocidade", Int16, queue_size=10, tcp_nodelay=True)     #Acelerador (+ --> frente, direção do garfo; - --> ré, direção AGV)
pub_direcao = rospy.Publisher("direcao_set", Int16, queue_size=10, tcp_nodelay=True)        #Direcao
#pub_garfo = rospy.Publisher("garfo_altura_set", Int16, queue_size=10, tcp_nodelay=True)     #Controle garfo
       
pub_syscommand = rospy.Publisher("/syscommand", String, queue_size=10)                  #Comandos para o hector_mapping (reset - reseta o mapa)
pub_marker = rospy.Publisher("marker", Marker, queue_size=10)                           #Para marcar no rviz
pub_iniciaFuncao = rospy.Publisher("inicio_funcao", Bool, queue_size=10)                #Para iniciar funções
pub_fim_funcao = rospy.Publisher("fim_funcao", Bool, queue_size=10)                     #Para finalizar funções
pub_acao = rospy.Publisher("acao", Int16, queue_size=10, tcp_nodelay=True)              #Para realizar ações
pub_enviar_msg_xbee = rospy.Publisher("enviar_msg_xbee", String, queue_size=10)  
pub_rotaAtual = rospy.Publisher("rota_atual", Int16, queue_size=10)                     #Rota atual
pub_idTag = rospy.Publisher("tag_atual", String, queue_size=10)                         #ID do ponto atual --> Para o supervisório, considera que os pontos de navegação são tags
pub_fuga = rospy.Publisher("fuga_rota", Bool, queue_size=10)                            #Indica se houve fuga de rota 
pub_erropos = rospy.Publisher("erro_pos", Bool, queue_size=10)                          #Indica se houve falha ao zerar erro
pub_erroplataforma = rospy.Publisher("erro_plataforma", Bool, queue_size=10)            #Indica se houve falha ao atuar na plataforma

pub_scanner = rospy.Publisher("trocar_scanner", Int16, queue_size=10)                   #Para trocar o scanner sendo usado atualmente para navegação e zerar erro

pub_areas_mod = rospy.Publisher("areas_mod", Int16, queue_size=10)                      #Para trocar as áreas do scanner durante a manobra de coleta

pub_parada_remota = rospy.Publisher("parada_remota", Bool, queue_size=10)               #Para parar remotamente, devido a erros

pub_reset_coleta = rospy.Publisher("rst_coleta", Bool, queue_size=10)                   #Para enviar o sinal de liberar balancelle
pub_reset_entrega = rospy.Publisher("rst_entrega", Bool, queue_size=10)                 #Para enviar o sinal de liberar taparella

#Feedback de funcionamento
pub_posicaoAtual = rospy.Publisher("posicao_atual", String, queue_size=10)
pub_posicaoObjetivo = rospy.Publisher("posicao_objetivo", String, queue_size=10)
pub_valoresNavegando = rospy.Publisher("valores_navegando", String, queue_size=10)
pub_angulos = rospy.Publisher("angulos", String, queue_size = 10)
pub_pontoAtual = rospy.Publisher("ponto_atual", String, queue_size=10)
pub_offset = rospy.Publisher("offsets", String, queue_size=10)



#------ CALLBACKS ------#
#Callback de /poseupdate, para saber a posição atual do AGV em relação ao mapa
def pose_callback(data):
    global pos_x, pos_y, roll, pitch, yaw, yaw_graus, offset_x, offset_y, offset_yaw
    #if(estadoAtual == "Rodando"):
    
    #Base:
    #pos_x = data.pose.pose.position.x + offset_x
    #pos_y = data.pose.pose.position.y + offset_y
    
    x_map = data.pose.pose.position.x
    y_map = data.pose.pose.position.y
    
    quaternion = (
        data.pose.pose.orientation.x,
        data.pose.pose.orientation.y,
        data.pose.pose.orientation.z,
        data.pose.pose.orientation.w)
    
    roll, pitch, yaw = tf.transformations.euler_from_quaternion(quaternion) #Ângulos em radianos convertidos de quaternions
    yaw_graus = math.degrees(yaw) #+ offset_yaw #Transforma em graus

    if(yaw_graus < 0):              #Não deixa ser negativo
        yaw_graus = yaw_graus + 360
    if(yaw_graus > 360):
        yaw_graus = yaw_graus - 360
    
    #Baseado em rotação de eixos: https://en.wikipedia.org/wiki/Rotation_of_axes
    #x' = x*cos(theta) + y*sen(theta)
    #y' = -x*sen(theta) + y*cos(theta)
    #Sinais e x,y trocados pela disposição do scanner
    if(scanner_atual == 0): #Utiliza o scanner frontal, com rotação de 45 graus (horário) ~~ 48 graus?
        pos_x = x_map*0.707106 - y_map*0.707106 + offset_x
        pos_y = x_map*0.707106 + y_map*0.707106 + offset_y
        if(sentido == 1):
            giro_x = -4*math.cos(yaw)#+0.7*math.sin(yaw)
            giro_y = -4*math.sin(yaw)#-0.7*math.cos(yaw)
            pos_x = pos_x + giro_x
            pos_y = pos_y + giro_y
    elif(scanner_atual == 1):   #Utiliza o scanner traseiro, com rotação de -135 graus #RECALCULAR
        pos_y = -(-x_map*0.707106 + y_map*0.707106) + offset_x
        pos_x = -(x_map*0.707106 + y_map*0.707106) + offset_y
        
    pub_posicaoAtual.publish("X: " + str(pos_x) + "     Y: " + str(pos_y) + "     Yaw: " + str(yaw_graus)) #Publica posição atual    


cnt_garfo = 0
#Verifica se o garfo terminou de ir para a posição desejada
#Publicado com 20Hz
def garfo_ok_callback(data):
    global fim_curso, cnt_garfo
    if(data.data == True):
        if(cnt_garfo < 40):
            cnt_garfo = cnt_garfo + 1
        else:
            fim_curso = True
    else:
        fim_curso = False

#Indica se deve ou não esperar pelo garfo
def verifica_garfo_callback(data):
    global espera_garfo
    espera_garfo = data.data

#Para criar um ponto de navegação
def criaPonto_callback(data):
    cria_ponto(data.data)
    
    
def standby_callback(data):
    global rampa_aceleracao
    if(data.data == True):
        rampa_aceleracao = 0
    

def reiniciaNavegacao_callback(data):
    global id_prox, obj_x, obj_y, angulo_obj, id_atual
    if(data.data == True):
        id_atual = -1
        id_prox = Database.getMin("PontosPosicao", "ID")[0][0]
        prox = Database.getItem("PontosPosicao", "ID", "0")[0]

        print("Próximo ponto: " + str(id_prox))
        obj_x = prox[1]          #Posição em X do objetivo
        obj_y = prox[2]          #Posição em Y do objetivo
        angulo_obj = math.degrees(math.atan2((obj_y - pos_y), (obj_x - pos_x)))
        print("Obj_x = " + str(obj_x) + "       Obj_y = " + str(obj_y))
    

#Para mudar ponto inicial
def mudar_ponto_callback(data):
    global id_prox, obj_x, obj_y, angulo_obj, id_atual

    id_atual = data.data
    id_prox = Database.getItem("PontosPosicao", "ID", str(data.data))[0][4]
    obj_x = 0
    obj_y = 0
    
    print("ID atual = " + str(id_atual))

#Para forçar a troca de rota
def trocar_rota_callback(data):
    Database.updateItem("Rotas", "Rota1", str(data.data), "id", "1")
    print("Mudando rota atual para " + str(data.data))
    
def trocar_scanner_callback(data):
    global scanner_atual
    scanner_atual = data.data

def reduz_scanner_callback(data):
    global reduz_vel
    if(data.data == True):
        reduz_vel = True
    else:
        reduz_vel = False

#Para atualizar o estado atual
def estado_callback(data):
    global estadoAtual
    estadoAtual = data.data
    
def vel_callback(data):
    global velocidade
    
    velocidade = Database.getItem("Velocidades", "ID", str(data.data))[0][1]
    print("Velocidade trocada para: " + str(velocidade))

    
testando = False
def testeCentro_callback(data):
    global testando
    
    testando = True

    #Envia os valores para o motor
    pub_acelerador.publish(-50)  #60
    pub_direcao.publish(int(data.data)) #!!!


min_angle = 0
max_angle = 0
increment_angle = 0
ranges = []
numero_amostras = 66 #Aproximadamente 2 segundo de amostras
cnt = 0
values = [0]*(numero_amostras+1)
metodo_2_x = []
metodo_2_y = []
fim_metodo_2 = True
save_offset_flag = '-1'
compara_offset_flag = '-1'
delay_count = 45 #33 #Aproximadamente 1 segundo de delay
def getRawPontos_callback(data):
    global min_angle, max_angle, increment_angle, ranges, cnt, values
    global save_offset_flag, compara_offset_flag, offset_x, offset_y, offset_yaw
    global obj_x, obj, distancia_obj, angulo_obj, delay_count
    global metodo_2_x, metodo_2_y, fim_metodo_2
    
    min_angle = data.angle_min
    max_angle = data.angle_max
    increment_angle = data.angle_increment
    ranges = data.ranges
    
    #Metodo 2 ----------------------------------------
    if(fim_metodo_2 == True):
        #print("FIM METODO 2")
        metodo_2_x = [[] for i in range(len(ranges))]
        metodo_2_y = [[] for i in range(len(ranges))]
    #--------------------------------------------------
    
    #Impede de tentar fazer o zeramento de erros durante a troca de scanner
    if(con_funcao > 0):
        return
 
    if((int(save_offset_flag) >= 0) or (int(compara_offset_flag) >= 0)):
    
        #if(delay_count > 0):
        #    delay_count = delay_count - 1
        #    return
        if(andando == True):
            pub_acelerador.publish(0)  #Faz com o agv parado
            return
    
        fim_metodo_2 = False
        pub_acelerador.publish(0)  #Faz com o agv parado
        x_axis = []
        y_axis = []
        if(int(save_offset_flag) >= 0):
            dados = Database.getItem("SalvaZeraErro", "ID", str(save_offset_flag))[0]
        else:
            dados = Database.getItem("SalvaZeraErro", "ID", str(compara_offset_flag))[0]
        r_1 = dados[1]
        r_2 = dados[2]
        ang_1 = dados[3]
        ang_2 = dados[4]
        
        ajuste_angular = 0
        if(scanner_atual == 0):
            ajuste_angular = 45 #48?
        elif(scanner_atual == 1):
            ajuste_angular = -135
            
        for i, r in enumerate(ranges):
            ang = math.degrees(min_angle + i*increment_angle) + ajuste_angular
            #print("Angulo corrigido: " + str(ang))
            if(r >= r_1 and r <= r_2 and (ang <= ang_1 and ang >= ang_2)):
                x_axis.append((r*math.cos(min_angle + i*increment_angle + math.radians(ajuste_angular))))
                y_axis.append((r*math.sin(min_angle + i*increment_angle + math.radians(ajuste_angular))))

        
        tamanho = len(x_axis)
        print("Tamanho total: " + str(tamanho))
        fisrt_third = 20 #int(tamanho/3)
        last_third = tamanho - 20 #tamanho - int(tamanho/3) 
        
        x_axis = x_axis[fisrt_third:last_third]
        y_axis = y_axis[fisrt_third:last_third]
        
        #Metodo 2--------------------------
        for i, item in enumerate(x_axis):
            try:
                metodo_2_x[i].append(item)
            except Exception as ex:
                print("Erro metodo 2 X: " + str(ex))
        for i, item in enumerate(y_axis):
            try:
                metodo_2_y[i].append(item)
            except Exception as ex:
                print("Erro metodo 2 Y: " + str(ex))
        #----------------------------------
        
        #Estatísticas para remover outliers
        x_mean = statistics.mean(x_axis)
        y_mean = statistics.mean(y_axis)
        x_stdev = statistics.stdev(x_axis)
        y_stdev = statistics.stdev(y_axis)
        
        remove_item = False
        remove_list = []
        for i in range(len(x_axis)):
            remove_item = False
            if((x_axis[i] > (x_mean + 3*x_stdev)) or (x_axis[i] < (x_mean - 3*x_stdev))):
                remove_item = True
            if((y_axis[i] > (y_mean + 3*y_stdev)) or (y_axis[i] < (y_mean - 3*y_stdev))):
                remove_item = True
            if(remove_item == True):
                print(f'Removido: {x_axis[i]}, {y_axis[i]}, na posicao {i}, média x e y: {x_mean}  {y_mean}')
                remove_list.append(i)
                #x_axis.pop(i)
                #y_axis.pop(i)
        
        remove_list = list(reversed(remove_list))
        for item in remove_list:
            x_axis.pop(item)
            y_axis.pop(item)
  
        print("Tamanho reduzido: " + str(len(x_axis)))
        
        print(cnt)
        
        #values[cnt] = (math.degrees(math.atan2((y_axis[-1] - y_axis[0]),(x_axis[-1] - x_axis[0])))) #abs
        line = np.polyfit(x_axis,y_axis,1)
        values[cnt] = math.degrees(math.atan(line[0]))
        
        if(cnt == numero_amostras):
            f_yaw = 0
            for i, val in enumerate(values):
                print(f"Angulo = {val}")
                f_yaw = f_yaw + val
            
            f_yaw = f_yaw/(len(values))
            print(f'Yaw metodo 1: {f_yaw}')
            
            #Metodo 2 -----------------------------------------
            media_x = []
            media_y = []
            print("TAMANHO: " + str(len(metodo_2_x)))
            for i, item in enumerate(metodo_2_x):
                if(len(metodo_2_x[i]) > 0):
                    media_x.append(statistics.mean(metodo_2_x[i]))
                    media_y.append(statistics.mean(metodo_2_y[i]))
            
            metodo_2_line = np.polyfit(media_x,media_y,1)
            metodo_2_angle = math.degrees(math.atan(metodo_2_line[0]))
            print(f'Yaw metodo 2: {metodo_2_angle}')
            #---------------------------------------------------
            
            if(int(save_offset_flag) >= 0):
                print(f"Ponto {save_offset_flag} salvo com x = {x_axis[0]}, y = {y_axis[0]} e yaw = {f_yaw}")
                Database.insertOffsets(str(save_offset_flag), str(x_axis[0]), str(y_axis[0]), str(f_yaw))
                
            if(int(compara_offset_flag) >= 0):
                #Faz a comparação
                
                print(f"X atual = {x_axis[0]}   Y atual = {y_axis[0]}   Yaw atual = {f_yaw}")
                
                bd = Database.getItem("ZeraErro", "ID", str(compara_offset_flag))[0]
                print(bd)
                
                x_base = Database.getItem("ZeraErro", "ID", str(compara_offset_flag))[0][1]
                print("X base = " + str(x_base))
                
                y_base = Database.getItem("ZeraErro", "ID", str(compara_offset_flag))[0][2]
                print("Y base = " + str(y_base))
                
                yaw_base = Database.getItem("ZeraErro", "ID", str(compara_offset_flag))[0][3]
                print("Yaw base = " + str(yaw_base))
                
                offset_x = -(x_axis[0] - x_base)
                offset_y = -(y_axis[0] - y_base)
                offset_yaw = -(f_yaw - yaw_base)
                print("Offset x = " + str(offset_x))
                print("Offset y = " + str(offset_y))
                print("Offset yaw = " + str(offset_yaw))
                
                if(abs(offset_x) > 0.5 or abs(offset_y) > 0.5 or abs(offset_yaw) > 10):
                    #print("Erro ao zerar erro: valor muito alto")
                    pub_erropos.publish(True)
                
                
                #prox_pos = Database.getItem("PontosPosicao", "ID", str(id_prox))[0]
                prox_pos_ = Database.getItem2("ProximoPontosPosicao", "idPontosPosicao", str(id_prox), "Rota", str(rotaAtual))[0][3]
                
                if(prox_pos_ == None):
                    pub_fuga.publish(True)
                    return
                    
                prox_pos = Database.getItem("PontosPosicao", "ID", str(prox_pos_))[0]
                
                print(f"APOS ZERAR ERRO: Era X: {prox_pos[1]}    Era Y: {prox_pos[2]}") 
                
                obj_x = prox_pos[1]*math.cos(math.radians(offset_yaw)) + prox_pos[2]*math.sin(math.radians(offset_yaw))
                obj_y = -prox_pos[1]*math.sin(math.radians(offset_yaw)) + prox_pos[2]*math.cos(math.radians(offset_yaw))
                print(f"APOS ZERAR ERRO: Virou X: {obj_x}    Virou Y: {obj_y}")
                #print("ID atual: " + str(id_atual))
            
                angulo_obj = math.degrees(math.atan2((obj_y - pos_y), (obj_x - pos_x)))
    
                distancia_obj = math.sqrt(math.pow((obj_x - pos_x), 2) + math.pow((obj_y - pos_y), 2))
    
                pub_posicaoObjetivo.publish("Distancia: " + str(distancia_obj))
                pub_posicaoObjetivo.publish("Angulo: " + str(angulo_obj))
                pub_posicaoObjetivo.publish("Obj_x: " + str(obj_x) + "      Obj_Y: " + str(obj_y))
                
                pub_syscommand.publish("reset")
                
        if(cnt == numero_amostras):
            cnt = 0
            save_offset_flag = '-1'
            compara_offset_flag = '-1'
            delay_count = 33
            fim_metodo_2 = True
            print("Fim funcao de zerar erro")
            
        else:
            cnt = cnt+1

def viewPoints_callback(data):
    first = 0
    f_x = 0
    f_y = 0
    dados = Database.getItem("SalvaZeraErro", "ID", str(data.data))[0]
    print(dados)
    r_1 = dados[1]
    r_2 = dados[2]
    ang_1 = dados[3]
    ang_2 = dados[4]
    
    ajuste_angular = 0
    if(scanner_atual == 0):
        ajuste_angular = -45   #48?
    elif(scanner_atual == 1):
        ajuste_angular = 135
        
    for i, r in enumerate(ranges):
        ang = math.degrees(min_angle + i*increment_angle) + ajuste_angular
        #print("Angulo corrigido: " + str(ang))
        if(r >= r_1 and r <= r_2 and (ang <= ang_1 and ang >= ang_2)):
            if(first == 0):
                first = r
                print("Primeiro angulo: " + str(first))
                f_x = first*math.cos(min_angle + i*increment_angle + math.radians(ajuste_angular))
                f_y = first*math.sin(min_angle + i*increment_angle + math.radians(ajuste_angular))
                print("X = " + str(f_x))
                print("Y = " + str(f_y))
            if(r <= first):    
                print("Distancia: " + str(r) + " com angulo " + str(math.degrees(min_angle + i*increment_angle + math.radians(ajuste_angular))))
            #x_axis.append((r*math.cos(min_angle + i*increment_angle + math.radians(ajuste_angular))))
            #y_axis.append((r*math.sin(min_angle + i*increment_angle + math.radians(ajuste_angular))))



#last_dist = 0
last_map_x = 0
last_map_y = 0
count_map = 0
delay_encoder = 0
def encoder_callback(data):
    global count_map, last_map_x, last_map_y
    global andando, delay_encoder
    
    if(estadoAtual == "Rodando"):
        if(data.data != 0):
            #dist = math.sqrt(pos_x**2 + pos_y**2)
            if(abs(pos_x - last_map_x) < 0.1 and abs(pos_y - last_map_y) < 0.1):
                count_map = count_map+1
                if(count_map > 40):
                    #pub_fuga.publish(True)
                    print("Possível Fuga de Rota pelo mapa")
                    print(f'Dist_x: {pos_x}    last_dist_x: {last_map_x}')
                    print(f'Dist_y: {pos_y}    last_dist_y: {last_map_y}')
            else:
                count_map = 0
                last_map_x = pos_x
                last_map_y = pos_y
                #last_dist = math.sqrt(pos_x**2 + pos_y**2)
        else:
            count_map = 0
            last_map_x = pos_x
            last_map_y = pos_y
            #last_dist = math.sqrt(pos_x**2 + pos_y**2)
    else:
        count_map = 0
        last_map_x = pos_x
        last_map_y = pos_y
        #last_dist = math.sqrt(pos_x**2 + pos_y**2)
    
    #print("Encoder: " + str(data.data))
    if(data.data > 0.001):
        #print("Andando")
        andando = True
        delay_encoder = 0
    else:
        if(delay_encoder < 21):
            delay_encoder = delay_encoder + 1
        else:
            andando = False  
            #print("Parado")

            

def salva_offsets_callback(data):
    global save_offset_flag
    save_offset_flag = data.data


#Recebe um comando para zerar o erro
def zera_erro_callback(data):
    global compara_offset_flag
    if(data.data == "-1"):
        compara_offset_flag = id_atual
    else:
        compara_offset_flag = data.data
    #zera_erro(data.data)
        
#Recebe um ponto como objetivo
def point_callback(data):
    global id_atual, obj_x, obj_y, distancia_obj, angulo_obj, id_count, id_prox 
    
    id_obj = id_count 
    prox_id = id_count + 1
    id_count = id_count + 1
    Database.insertPontosPosicao(id_obj, data.point.x, data.point.y, '0', prox_id) #Por enquanto, nenhuma função
    
    n_pontos = Database.getAllItems("PontosPosicao")
    print("Número de pontos: " + str(len(n_pontos)))
    
    mark = Marker()
    mark.header.frame_id = "map"
    mark.ns = "Points"
    mark.id = id_obj
    mark.action = 0
    mark.type = 2
    mark.pose = Pose()
    mark.pose.position.x = data.point.x
    mark.pose.position.y = data.point.y
    mark.pose.orientation.x = 0
    mark.pose.orientation.y = 0
    mark.pose.orientation.z = 0
    mark.pose.orientation.w = 1
    mark.color.r = 1
    mark.color.a = 1
    mark.scale.x = 0.2
    mark.scale.y = 0.2
    mark.scale.z = 0.2
    pub_marker.publish(mark)

    if(id_prox == None):
        id_prox = id_obj
        obj_x = data.point.x
        obj_y = data.point.y
        angulo_obj = math.degrees(math.atan2((obj_y - pos_y), (obj_x - pos_x)))
        

#Para limpar todos os pontos cadastrados
def resetPontos_callback(data):
    global id_count
    if(data.data == True):
        try:
            Database.deleteAllItems("PontosPosicao")
            mark = Marker()
            mark.header.frame_id = "map"
            mark.ns = "Points"
            mark.action = 3
            pub_marker.publish(mark)
            print("Pontos deletados")
            id_count = 0
        except Exception as ex:
            print("Erro deletando pontos: " + str(ex))
            
def reseta_offset_callback(data):
    global offset_x, offset_y, offset_yaw
    if(data.data == True):
        offset_x = 0
        offset_y = 0
        offset_yaw = 0
  
#Para linkar dois pontos
def linkPontos_callback(data):
    pontos = (data.data).split()
    if(len(pontos) > 2):
        return
    Database.updateItem("PontosPosicao", "ProxID", str(pontos[1]), "ID", str(pontos[0]))
    print("Ponto " + str(pontos[0]) + " linkado com ponto "  + str(pontos[1]))
        

def addFuncao_callback(data):
    termos = data.data.split(" ") #Divide: primeira parte função, segunda parte ID
    try:
        Database.updateItem("PontosPosicao", "Funcao", str(termos[0]), "ID", str(termos[1]))
    except:
        pass

def sem_funcao_callback(data):
    try:
        Database.updateItem("PontosPosicao", "Funcao", "0", "ID", str(data.data))
    except:
        pass

def sentido_callback(data):
    global sentido
    if(data.data == True):
        sentido = 1
    else:
        sentido = -1

def troca_pid_callback(data):
    global kp, kd, ki
    new_pid = Database.getItem("PID", "ID", str(data.data))
    
    kp = new_pid[0][1]
    ki = new_pid[0][2]
    kd = new_pid[0][3]
    print("Novo pid: ")
    print("KP = " + str(kp))
    print("KD = " + str(kd))
    print("KI = " + str(ki))
    

def quase_coleta_callback(data):
    global quase_coleta
    quase_coleta = data.data

def pronto_coleta_callback(data):
    global pronto_coleta
    pronto_coleta = data.data

def parada_coleta_callback(data):
    global parada_coleta
    parada_coleta = data.data
    
def quase_entrega_callback(data):
    global quase_entrega
    quase_entrega = data.data

def pronto_entrega_callback(data):
    global pronto_entrega
    pronto_entrega = data.data
    
def parada_entrega_callback(data):
    global parada_entrega
    parada_entrega = data.data

#------- FUNÇÕES -------#

def cria_ponto(data):
    global id_atual, distancia_obj, angulo_obj, id_count, id_prox 
    if(data == True):
        id_obj = id_count 
        prox_id = id_count + 1
        id_count = id_count + 1
        temp_x = pos_x*math.cos(math.radians(-offset_yaw)) + pos_y*math.sin(math.radians(-offset_yaw))
        temp_y = -pos_x*math.sin(math.radians(-offset_yaw)) + pos_y*math.cos(math.radians(-offset_yaw))
        Database.insertPontosPosicao(id_obj, temp_x, temp_y, '0', prox_id) #Por enquanto, nenhuma função
        
        n_pontos = Database.getAllItems("PontosPosicao")
        print("Ponto " + str(id_obj) + " criado em: " + str(temp_x) + ", " + str(temp_y))
        print("Número de pontos: " + str(len(n_pontos)))

#Realizar marcações no rviz
def interacao_rviz_callback(data):
    try:
        todos_pontos = Database.getAllItems("PontosPosicao")
        print("Todos os pontos: " + str(todos_pontos))
        for pontos in todos_pontos:
            mark = Marker()
            mark.header.frame_id = "map"
            mark.ns = "Points"
            mark.id = pontos[0]
            mark.action = 0
            mark.type = 2
            mark.pose = Pose()
            mark.pose.position.x = pontos[1]
            mark.pose.position.y = pontos[2]
            mark.pose.orientation.x = 0
            mark.pose.orientation.y = 0
            mark.pose.orientation.z = 0
            mark.pose.orientation.w = 1
            mark.color.r = 1
            mark.color.a = 1
            mark.scale.x = 5
            mark.scale.y = 5
            mark.scale.z = 5
            pub_marker.publish(mark)
    except Exception as ex:
        print("Erro ao criar marker: " + str(ex))

def encontra_pos_inicial():
    global obj_x, obj_y, id_prox, id_count, angulo_obj
    try:
        #Por enquanto, considera que começa no ponto 0
        prox = Database.getItem("PontosPosicao", "ID", "0")[0]
        print(prox)
        id_prox = 0
        print("Próximo ponto: " + str(id_prox))
        obj_x = prox[1]          #Posição em X do objetivo
        obj_y = prox[2]          #Posição em Y do objetivo
        angulo_obj = math.degrees(math.atan2((obj_y - pos_y), (obj_x - pos_x)))
    
    except Exception as ex:
        id_prox = 0
        obj_x = 0
        obj_y = 0
        print("Próximo ponto não encontrado: " + str(ex))

    try:
        id_count = Database.getMax("PontosPosicao", "ID")[0][0] + 1
        print("ID count = " + str(id_count))
    except Exception as ex:
        id_count = 0
        print("ID count não inicializado: " + str(ex))

    if (id_count is None):
        print("Inicializado como 0, ao invés de None")
        id_count = 0 


#Valores provenientes do callback do scanner
'''
def re_coleta():
    ajuste_angular = 0
    if(scanner_atual == 0):
        ajuste_angular = -45
    elif(scanner_atual == 1):
        ajuste_angular = 135 #45
    
    x_axis = []
    y_axis = []
    angulos = [] 
    for i, r in enumerate(ranges):
        ang = math.degrees(min_angle + i*increment_angle) + ajuste_angular
        if(ang > 180): #(ang < 90 or ang > -90) 
            print(ang)
            x_axis.append((r*math.cos(min_angle + i*increment_angle + math.radians(ajuste_angular))))
            y_axis.append((r*math.sin(min_angle + i*increment_angle + math.radians(ajuste_angular))))
            angulos.append(ang)
    
    retas = [[],[]]
    retas_cont = 0
    for i, item in enumerate(x_axis):
        try:
            if(abs(x_axis[i] - x_axis[i+1]) < 0.2):
                retas[retas_cont].append((x_axis[i], y_axis[i]))
            else:
                retas_cont += 1
                print(f'Numero de retas: {retas_cont}')
                retas[retas_cont].append((x_axis[i], y_axis[i]))
    
    max_line = 0
    true_line = []
    for line in retas:
        if len(line) > max_line:
            max_line = len(line)
            true_line = line
    
    mid_value = line[int(len(line)/2)][1]
    print(f'mid_value: {mid_value}')
    
    #Usar o valor do meio para navegar de ré
    
    
        
    pass
 '''

def zera_erro(id_n):
    global offset_x, offset_y, offset_yaw, compara_offset_flag
    #Ver todos os pontos que estão abaixo de certo valor (e dentro de uma faixa)
    #Ver primeiro(s) e último(s) ponto(s)
        #Ver variação: onde deveria estar e onde estão
        #Ver angulação entre esses pontos
    print("Funcao de zerar erro: " + str(id_n))
    #pub_syscommand.publish("reset")
    offset_x = 0
    offset_y = 0
    offset_yaw = 0
    compara_offset_flag = id_n
  

#Calcula o erro angular 
def calcula_erro_angular():
    global angulo_obj, yaw_graus
    
    erro = angulo_obj - yaw_graus  #Calcula o erro
    
    if(erro < -180):        #Não deixa fora da faixa (o valor vai de -180 até +180)
        erro = erro + 360
        
    if(sentido == 1 and erro > 0):
        erro = erro - 180
    elif(sentido == 1 and erro < 0):
        erro = erro + 180
    
    return erro


last_x = 0
last_y = 0

#Navegação
kp = 5 #5 #0.2    #Valor para o Kp do PID
kd = 0      #Valor para o Kd do PID
ki = 0      #Valor para o Ki do PID
proporcional = 0    #Resultado proporcional do PID
integrativo = 0     #Resultado integrativo do PID
derivativo = 0      #Resultado derivativo do PID
erro_0 = 0          #Erro anterior
last_T = time.time()#Tempo anterior para cálculo do PID
T_pid = 0           #Variação entre o tempo atual e o último tempo (não precisva ser global, na verdade)
limIntegral = 5     #Limite do valor integral
def navegacao():
    global id_atual, id_prox, funcao, distancia_obj, yaw_graus, limIntegral, angulo_obj, obj_x, obj_y
    global kp, kd, ki, proporcional, integrativo, derivativo, erro_0, T_pid, last_T, id_atual, z, delay_garfo, fim_curso
    global last_x, last_y, passo_funcao, offset_x, offset_y, offset_yaw, margem, id_function, con_funcao, rampa_aceleracao
    global enable_parada_coleta, enable_parada_entrega, espera_garfo
    
    if(testando == True):
        return
        
    if((enable_parada_coleta and parada_coleta) or (enable_parada_entrega and parada_entrega)):
        pub_parada_remota.publish(True)
    else:
        pub_parada_remota.publish(False)
        
    
    #Só aplica a lógica de navegação no estado Rodando
    if(estadoAtual == "Rodando"):
        
        #erro = calcula_erro_angular()   #Calcula o erro angular
        T_pid = time.time() - last_T    #Calcula o tempo para o PID 

        angulo_obj = math.degrees(math.atan2((obj_y - pos_y),(obj_x - pos_x)))
        distancia_obj = math.sqrt(math.pow((obj_x - pos_x), 2) + math.pow((obj_y - pos_y), 2)) #Recalcula o erro linear (distância até o objetivo)
        
        erro = calcula_erro_angular()   #Calcula o erro angular
        print("Erro angular: " + str(erro))
            
        
        pub_valoresNavegando.publish("d_obj: " + str(distancia_obj) + "     Erro: " + str(erro)) #Feedback da distância até o objetivo
        
        #Caso esteja mais distante que Xcm, continua navegando
        if(distancia_obj > margem):
        
            if(abs(erro) > 120): 
            #    pub_fuga.publish(True)
                print("!!!POSSIVEL FUGA DE ROTA POR PONTO!!!")

            proporcional = erro * kp                        #Valor do resultado proporcional
            integrativo = integrativo + erro * ki * T_pid   #Valor do resultado integrativo
            derivativo = (erro - erro_0) * kd / T_pid       #Valor do resultado derivativo
            erro_0 = erro                                   #Atualiza erro anterior
            
            #Impede o valor integrativo de crescer muito
            if(integrativo >= limIntegral):
                integrativo = limIntegral                   
            elif(integrativo < -limIntegral):
                integrativo = -limIntegral
                
            #Zera valor integrativo em torno do ângulo objetivo
            if(yaw_graus > -15 and yaw_graus < 15):
                integrativo = 0
            
            #Soma as partes do PID
            z = CENTRO_DIRECAO + (sentido * (proporcional + integrativo + derivativo)) #Considera o centro da direção como não sendo o 0
            #z = 0
            
            pub_valoresNavegando.publish("Z = " + str(z) + " com " + str((proporcional + integrativo + derivativo)) + " de correcao")
            #z = 153
            #print("Valor de z = " + str(z))
            
            
            #Impede a correção de ser muito forte (por enquanto, está igual ao manual)
            if(z > limite_direcao_superior):
                z = limite_direcao_superior
            elif(z < limite_direcao_inferior):
                z = limite_direcao_inferior


            #print("save_offset_flag = " + str(save_offset_flag))
            #print("compara_offset_flag = " + str(compara_offset_flag))
            #Envia os valores para o motor
            if(int(save_offset_flag) == -1 and int(compara_offset_flag) == -1):
                if(espera_garfo == False):
                    if(reduz_vel == True and velocidade >= 60):
                        pub_acelerador.publish(sentido * 40)          #Velocidade de redução
                        rampa_aceleracao = 0.6              #Avança na rampa de aceleração
                    elif(velocidade >= 60):
                        pub_acelerador.publish(sentido * int(velocidade * rampa_aceleracao))  #60
                    else:
                        pub_acelerador.publish(sentido * velocidade)  #Menor que 60
                        
                    if(rampa_aceleracao < 1):
                        rampa_aceleracao = rampa_aceleracao + 0.025
                        
                    pub_direcao.publish(int(z)) #!!!
                else:
                    pub_acelerador.publish(0) #Para até o garfo ficar estável
                    if(fim_curso == True):
                        espera_garfo = False
                        
            
                
            last_T = time.time() #Atualiza o último tempo
        else:
            #Chegou perto o suficiente do objetivo
            
            if(id_atual == -1):
                id_atual = 0
            
            print("Chegou no ponto objetivo")
            try:
                print("Executando funcoes do ponto " + str(id_prox))
                #do_func = Database.getItem("PontosPosicao", "ID", str(id_prox))[0]
                #do_func_ = Database.getItem2("Funcoes", "IdPontosPosicao", str(id_prox), "Rota", str(rotaAtual))
                #if(do_func_ == []):
                #    do_func_ = Database.getItem2("Funcoes", "IdPontosPosicao", str(id_prox), "Rota", "0")
                do_func_ = Database.getFuncoes(str(rotaAtual), str(id_prox))
                print("do_func_: " + str(do_func_))
                todas_funcoes = [item[3] for item in do_func_]
                print("todas_funcoes: " + str(todas_funcoes))
                #todas_funcoes = do_func[3].split("#")
                #Funções especiais de navegação, as funções "normais" estão no arquivo Estados.py
                for f in todas_funcoes:
                    print("teste: " + str(f))
                    f = str(f)
                    if("especial" in f):                #Manobras e e funções com vários passos
                        passo_funcao = 0
                        id_function = id_prox
                        pub_iniciaFuncao.publish(True)
                        funcao = f
                        print("Funcao de navegacao encontrada: " + funcao) 
                    #-----------------------------------------------------------------------------------------------------------
                    elif(f == "zera_erro"):             #Para zerar o erro
                        passo_funcao = 0
                        print("Funcao para zerar erro")
                        zera_erro(id_prox)
                    #-----------------------------------------------------------------------------------------------------------
                    elif("pid" in f):                   #Trocar PID (e margem, dependendo)
                        if("1" in f):
                            kp = 0.5#0.8
                            #margem = 0.15
                        elif("2" in f):
                            kp = 0.8
                        elif("3" in f):
                            kp = 1.2
                        elif("4" in f):
                            kp = 2
                            #margem = 0.05
                        print("Kp = " + str(kp))
                    #-----------------------------------------------------------------------------------------------------------
                    elif("margem" in f):                #Trocar margem de aceitação 
                        if("1" in f):
                            margem = 0.01
                        elif("2" in f):
                            margem = 0.05
                        elif("3" in f):
                            margem = 0.1
                        elif("4" in f):
                            margem = 0.15
                        print("Margem = " + str(margem))
                    #-----------------------------------------------------------------------------------------------------------
                    #elif("scanner" in f):           #Trocar de scanner para navegação
                    #    if("0" in f):
                    #        pub_scanner.publish(0)  #Scanner frontal
                    #        #con_funcao = 80
                    #    elif("1" in f):
                    #        #con_funcao = 80
                    #        pub_scanner.publish(1)  #Scanner traseiro
                    #-----------------------------------------------------------------------------------------------------------
                    elif("inicio_area_coleta" in f):
                        enable_parada_coleta = True
                    elif("inicio_area_entrega" in f):
                        enable_parada_entrega = True
                    elif("fim_area_coleta" in f):
                        enable_parada_coleta = False
                    elif("fim_area_entrega" in f):
                        enable_parada_entrega = False
                    #-----------------------------------------------------------------------------------------------------------
                    elif("reset_coleta" in f):
                        pub_reset_coleta.publish(True)
                    elif("reset_entrega" in f):
                        pub_reset_entrega.publish(True)
                    #-----------------------------------------------------------------------------------------------------------
                    elif("reset_scanner" in f):
                        print("Tipo de scanner resetado")
                        pub_areas_mod.publish(1) #Volta para o tipo de scanner em que a área interna para, intermediaria e externa reduz
                    #-----------------------------------------------------------------------------------------------------------
                    elif(f != '0'):                     #Funções "normais" (ver Estados.py)
                        pub_acao.publish(int(f))
            except Exception as ex:
                print("Sem função: " + str(ex))
                
            
            #prox_pos = Database.getItem("PontosPosicao", "ID", str(id_atual))[0]
            id_func = id_atual
            id_atual = id_prox
            print("ID atual: " + str(id_atual))
            
            #id_prox = Database.getItem("PontosPosicao", "ID", str(id_atual))[0][4]
            #print("ID prox: " + str(id_prox)) 
            
            try:
                if(id_func == -1):
                    id_func = 0
                
                prox_pos_ = Database.getItem2("ProximoPontosPosicao", "idPontosPosicao", str(id_atual), "Rota", str(rotaAtual))
                print(prox_pos_)
                
                if(prox_pos_ == []):
                    prox_pos_ = Database.getItem2("ProximoPontosPosicao", "idPontosPosicao", str(id_atual), "Rota", "0")
                    print("Procurando na rota 0")
                    print(prox_pos_)
                    if(prox_pos_ == []):
                        pub_fuga.publish(True)
                        return
                        
                prox_pos_ = prox_pos_[0][3]
                                   
                prox_pos = Database.getItem("PontosPosicao", "ID", str(prox_pos_))[0]
                id_prox = prox_pos_
                print("ID prox: " + str(id_prox))
                
                #prox_pos = Database.getItem("PontosPosicao", "ID", str(id_prox))[0]
                #obj_x = prox_pos[1]
                #obj_y = prox_pos[2]
                print(f"Era X: {prox_pos[1]}    Era Y: {prox_pos[2]}") 
                obj_x = prox_pos[1]*math.cos(math.radians(offset_yaw)) + prox_pos[2]*math.sin(math.radians(offset_yaw))
                obj_y = -prox_pos[1]*math.sin(math.radians(offset_yaw)) + prox_pos[2]*math.cos(math.radians(offset_yaw))
                print(f"Virou X: {obj_x}    Virou Y: {obj_y}")
                #print("ID atual: " + str(id_atual))
            
                angulo_obj = math.degrees(math.atan2((obj_y - pos_y), (obj_x - pos_x)))
    
                distancia_obj = math.sqrt(math.pow((obj_x - pos_x), 2) + math.pow((obj_y - pos_y), 2))
    
                pub_posicaoObjetivo.publish("Distancia: " + str(distancia_obj))
                pub_posicaoObjetivo.publish("Angulo: " + str(angulo_obj))
                pub_posicaoObjetivo.publish("Obj_x: " + str(obj_x) + "      Obj_Y: " + str(obj_y))
            
                
            except Exception as ex:
                print("Não há próximo ponto, finalizando: " + str(ex))
                id_prox = None
                pub_acao.publish(2) #Envia "Parada automática"
            #print("Menor que 0.3")
            #pub_motor1.publish(0)
            #pub_motor2.publish(0)
        
        
val_dir = CENTRO_DIRECAO #Para manter e escalonar o valor da direção entre intervalos de função
con_dir = 0
def executa_funcao():
    global funcao, con_funcao, passo_funcao, offset_x, offset_y, offset_yaw
    global snap_x, snap_y, snap_yaw, val_dir, mensagem_recebida, con_dir, con_erro_plataforma
    
    if(estadoAtual == "Funcao"):
        
        #Espera dar o delay estabelecido
        if(con_funcao > 0):
            con_funcao -= 1
            #print("Con_funcao: " + str(con_funcao))
            return

            
        #-----------------------------------------------------------------------------------------------------------------------
        '''
        if(funcao == "especial_coleta"):      #Coleta
            print("Funcao de coleta")
            if(passo_funcao == 0):                          #Para       
                print("Passo 0")
                pub_acelerador.publish(0)
                passo_funcao = 1
                con_funcao = DELAY_ENTRE_ACOES  
                #pub_areas_mod.publish(2) #Todas as áreas param
                #snap_x = pos_x
                #snap_y = pos_y
                #snap_yaw = yaw_graus
            elif(passo_funcao == 1 and con_funcao == 0):    #Ajusta posição da direção   
                print("Passo 1")
                pub_direcao.publish(0)
                passo_funcao = 2
                con_funcao = DELAY_ENTRE_ACOES
            elif(passo_funcao == 2 and con_funcao == 0):    #Gira
                print("Passo 2 -- Yaw: " + str(yaw_graus))
                pub_frente.publish(False)
                pub_reverso.publish(True)
                if(yaw_graus < 80 or yaw_graus > 300):
                    pub_acelerador.publish(60) 
                elif(yaw_graus < (90 - offset_yaw)): #89.5
                    pub_acelerador.publish(25) 
                else:
                    pub_acelerador.publish(0)
                    snap_y = pos_y
                    con_funcao = 0
                    passo_funcao = 3
            elif(passo_funcao == 3 and con_funcao == 0):    #Para e centraliza direção
                print("Passo 3")
                pub_acelerador.publish(0)
                pub_direcao.publish(val_dir) # CENTRO_DIRECAO + 1
                passo_funcao = 4 #4
                con_erro_plataforma = 0
                con_funcao = DELAY_ENTRE_ACOES
                pub_acao.publish(17) #Muda para a área 4 do scanner (ré)
            elif(passo_funcao == 80 and con_funcao == 0):    #Abaixa o garfo
                print("Passo 80")
                pub_levanta_garfo.publish(False)
                pub_abaixa_garfo.publish(True)
                passo_funcao = 81
                con_funcao = DELAY_ENTRE_ACOES #+ 24
            elif(passo_funcao == 81 and con_funcao == 0): #Termina de abaixar o garfo
                print("Passo 81")
                if(fim_curso == False):
                    pub_levanta_garfo.publish(False)
                    pub_abaixa_garfo.publish(True)
                    #con_erro_plataforma = con_erro_plataforma + 1
                    #if(con_erro_plataforma >= LIM_ERRO_PLATAFORMA):
                    #    pub_erroplataforma.publish(True)
                else:
                    passo_funcao = 4 #3
                    con_funcao = DELAY_ENTRE_ACOES
            elif(passo_funcao == 4 and con_funcao == 0):    #Avança de ré
                print("Passo 4 -- Pos_Y: " + str(abs(pos_y - snap_y)))
                if(quase_coleta == False or pronto_coleta == False):
                    pub_acelerador.publish(0) 
                    print("Sinal de coleta quase-pronta ou pronta não acionado")
                    return
                if(con_dir == 0):
                    val_dir = CENTRO_DIRECAO+1
                    con_dir = 3
                else:
                    val_dir = CENTRO_DIRECAO
                    con_dir = con_dir - 1
                pub_direcao.publish(val_dir)
                pub_frente.publish(True)
                pub_reverso.publish(False)
                pub_levanta_garfo.publish(False)    #Reseta garfo
                pub_abaixa_garfo.publish(False)     #Reseta garfo     
                if(abs(pos_y - snap_y) < 1.3111): #1.411
                    pub_areas_mod.publish(2) #Todas as áreas param
                elif(abs(pos_y - snap_y) < 2.1): #2.2
                    pub_areas_mod.publish(3) #Interna e intermediaria
                elif(abs(pos_y - snap_y) < 2.7643): #2.86
                    pub_areas_mod.publish(4) #Somente interna
                else:
                    #pub_areas_mod.publish(4) #Somente interna
                    pub_acao.publish(15)
                if(abs(pos_y - snap_y) < 2.9143): #2.59
                    pub_acelerador.publish(60) 
                elif(abs(pos_y - snap_y) < 4.39): #4.34
                    pub_acelerador.publish(30) 
                else:
                    pub_acelerador.publish(0)
                    con_funcao = DELAY_ENTRE_ACOES
                    passo_funcao = 5
            elif(passo_funcao == 5 and con_funcao == 0):    #Levanta garfo
                print("Passo 5")
                pub_areas_mod.publish(4) #Ignorar áreas externa e intermediária
                pub_levanta_garfo.publish(True)
                pub_abaixa_garfo.publish(False)
                con_erro_plataforma = 0
                passo_funcao = 6
                con_funcao = DELAY_ENTRE_ACOES
            elif(passo_funcao == 6 and con_funcao == 0):    #Termina de levantar o garfo
                print("Passo 6")
                if(fim_curso == False):
                    pub_levanta_garfo.publish(True)
                    pub_abaixa_garfo.publish(False)
                    #con_erro_plataforma = con_erro_plataforma + 1
                    #if(con_erro_plataforma >= LIM_ERRO_PLATAFORMA):
                    #    pub_erroplataforma.publish(True)
                else:
                    zera_erro(id_function)
                    passo_funcao = 7
                    con_funcao = DELAY_ENTRE_ACOES
            elif(passo_funcao == 7 and con_funcao == 0 and compara_offset_flag == "-1"):
                    pub_fim_funcao.publish(True)
                    funcao = "0"
                    #pub_acao.publish(2)
        '''
                        
                  
if __name__ == '__main__':
    rospy.init_node('Navegacao', anonymous=False)
    rospy.Subscriber("/poseupdate", PoseWithCovarianceStamped, pose_callback, queue_size=10, buff_size=2**24)
    rospy.Subscriber("estado", String, estado_callback, queue_size=10)
    rospy.Subscriber("/clicked_point", PointStamped, point_callback, queue_size=10)
    rospy.Subscriber("troca_velocidade", Int16, vel_callback)
    rospy.Subscriber("teste_centro", Int16, testeCentro_callback)
    rospy.Subscriber("/sick_safetyscanners/scan", LaserScan, getRawPontos_callback, queue_size=10) 
    rospy.Subscriber("zera_erro", String, zera_erro_callback, queue_size=10)
    rospy.Subscriber("reduz_scanner", Bool, reduz_scanner_callback, queue_size=10)
    rospy.Subscriber("standby", Bool, standby_callback, queue_size=10)
    rospy.Subscriber("agv_encoder", Float32, encoder_callback, queue_size=10)
    rospy.Subscriber("garfo_ok", Bool, garfo_ok_callback, queue_size=10)
    rospy.Subscriber("sentido", Bool, sentido_callback, queue_size=10)
    rospy.Subscriber("troca_pid", Int16, troca_pid_callback, queue_size=10)
    rospy.Subscriber("verifica_garfo", Bool, verifica_garfo_callback, queue_size=10)
    
    rospy.Subscriber("quase_coleta", Bool, quase_coleta_callback, queue_size=1)
    rospy.Subscriber("pronto_coleta", Bool, pronto_coleta_callback, queue_size=1)
    rospy.Subscriber("quase_entrega", Bool, quase_entrega_callback, queue_size=1)
    rospy.Subscriber("pronto_entrega", Bool, pronto_entrega_callback, queue_size=1)
    rospy.Subscriber("parada_coleta", Bool, parada_coleta_callback, queue_size=1)
    rospy.Subscriber("parada_entrega", Bool, parada_entrega_callback, queue_size=1)

    
    #Funções de suporte
    rospy.Subscriber("reset_pontos", Bool, resetPontos_callback, queue_size=10)
    rospy.Subscriber("link_pontos", String, linkPontos_callback, queue_size=10)
    rospy.Subscriber("cria_ponto", Bool, criaPonto_callback, queue_size=10)
    rospy.Subscriber("reinicia_navegacao", Bool, reiniciaNavegacao_callback, queue_size=10)
    rospy.Subscriber("add_funcao", String, addFuncao_callback, queue_size=10)
    rospy.Subscriber("sem_funcao", String, sem_funcao_callback, queue_size=10)
    rospy.Subscriber("salva_offsets", String, salva_offsets_callback, queue_size=10)
    rospy.Subscriber("clear_offset", Bool, reseta_offset_callback, queue_size=10)
    rospy.Subscriber("mudar_ponto", String, mudar_ponto_callback, queue_size=10)
    rospy.Subscriber("ver_pontos", String, viewPoints_callback, queue_size=10)
    
    rospy.Subscriber("trocar_rota", Int16, trocar_rota_callback, queue_size=10)
    rospy.Subscriber("trocar_scanner", Int16, trocar_scanner_callback, queue_size=10)
    
    rospy.Subscriber("interacao_rviz", Bool, interacao_rviz_callback, queue_size=10)
    

    
    #interacao_rviz()
    todos_pontos = Database.getAllItems("PontosPosicao")
    print("Todos os pontos: " + str(todos_pontos))
    
    encontra_pos_inicial()
    
    

    rate = rospy.Rate(20) #20Hz --> A cada 50ms
    while not rospy.is_shutdown():
        navegacao()
        executa_funcao()
        rotaAtual = Database.getAllItems("Rotas")[0][1]
        pub_rotaAtual.publish(int(rotaAtual))
        pub_idTag.publish(str(id_atual))
        pub_angulos.publish("Angulo agv: " + str(yaw_graus) + "     Angulo Obj.: " + str(angulo_obj)) #Feeedback dos ângulos atuais
        pub_pontoAtual.publish("Ponto atual: " + str(id_atual) + "      Prox ponto: " + str(id_prox))
        pub_posicaoObjetivo.publish("Obj_x: " + str(obj_x) + "      Obj_Y: " + str(obj_y))
        pub_offset.publish("X: " + str(offset_x) + "    Y: " + str(offset_y) + " Yaw: " + str(offset_yaw))
        
        #if(abs(angulo_obj - yaw_graus)>175):
        #    pub_fuga.publish(True)
        #else:
        #    pub_fuga.publish(False)
        
        rate.sleep()