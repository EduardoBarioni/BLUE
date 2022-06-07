#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from std_msgs.msg import Bool
from std_msgs.msg import Int16
from std_msgs.msg import Float32
from std_msgs.msg import Float64
from std_msgs.msg import UInt32
from sick_safetyscanners.msg import OutputPathsMsg
from geometry_msgs.msg import Twist
from geometry_msgs.msg import PoseWithCovarianceStamped
from subprocess import Popen, PIPE
import Database


#Publishers ----------------------------------------------------------------------------------------------------
pub_interlock = rospy.Publisher("interlock", Bool, queue_size=10, tcp_nodelay=True) #Interlock
pub_acoplar = rospy.Publisher("carregar", Bool, queue_size=10, tcp_nodelay=True)    #Carregador - Carregar
pub_desacoplar = rospy.Publisher("desacoplar", Bool, queue_size=10, tcp_nodelay=True)   #Carregador - Desacoplar
pub_estado = rospy.Publisher("estado", String, queue_size=10, tcp_nodelay=True) #Estado
pub_trocaVelocidade = rospy.Publisher("troca_velocidade", Int16, queue_size=10, tcp_nodelay=True)   #Troca velocidade e PID
pub_acao = rospy.Publisher("acao", Int16, queue_size=10, tcp_nodelay=True)  #Acao
pub_angle = rospy.Publisher("angulo", Int16, queue_size=10, tcp_nodelay=True)   #Valor do angulo da direcao
pub_encoderReset = rospy.Publisher("agv_encoder_dist_zerar", Bool, queue_size=10)   #Zerar distancia
pub_enviar_msg = rospy.Publisher("enviar_msg_xbee", String, queue_size=10)  #Enviar mensagem via Xbee
pub_funcao = rospy.Publisher("funcao_atual", String, queue_size=10) #Enviar funcao para natural
pub_syscommand = rospy.Publisher("/syscommand", String, queue_size=10)  #Para resetar mapa
pub_zera_erro = rospy.Publisher("zera_erro", String, queue_size=10) #Para executar a função de zerar erro
pub_reduz = rospy.Publisher("reduz_scanner", Bool, queue_size=10)#Para reduzir velocidade por scanner
pub_standby = rospy.Publisher("standby", Bool, queue_size=10)   #Indica se está parado
pub_reset_navegacao = rospy.Publisher("reinicia_navegacao", Bool, queue_size=10)    #Indica se deve reinicar a navegação
pub_pisca_feedback = rospy.Publisher("pisca_feedback", Bool, queue_size=10)    #Indica se deve piscar os leds para indicação
pub_reset_navegacao = rospy.Publisher("reinicia_navegacao", Bool, queue_size=10)    #Indica se deve reiniciar a navegação
pub_frente = rospy.Publisher("sentido", Bool, queue_size=10)    #Indica sentido que deve andar
pub_pid = rospy.Publisher("troca_pid", Int16, queue_size=10)    #Indica que o valor do PID deve ser trocado
pub_verifica_garfo = rospy.Publisher("verifica_garfo", Bool, queue_size=10) #Indica que deve verificar se o garfo está parado para se mover

pub_trocar_rota = rospy.Publisher("trocar_rota", Bool, queue_size=10)#trocar_rota

pub_garfo = rospy.Publisher("garfo_altura_set", Int16, queue_size=10, tcp_nodelay=True)     #Controle garfo


pub_buzzer = rospy.Publisher("agv_p4", Bool, queue_size=10, tcp_nodelay=True)   #Aciona Buzzer
pub_seguranca_acelerador = rospy.Publisher("agv_p7", Bool, queue_size=10, tcp_nodelay=True) #Aciona Segurança Acelerador
pub_buzina = rospy.Publisher("agv_p8", Bool, queue_size=10, tcp_nodelay=True)   #Aciona Buzina
pub_desliga = rospy.Publisher("agv_p12", Bool, queue_size=10, tcp_nodelay=True) #Aciona Desliga Equipamento
pub_desliga_temporizado = rospy.Publisher("agv_p12", Bool, queue_size=10, tcp_nodelay=True) #Desliga Temporizado
pub_hab_locomocao = rospy.Publisher("agv_p14", Bool, queue_size=10, tcp_nodelay=True)   #Habilita Movimentação
pub_sel_scanner_4 = rospy.Publisher("agv_p51", Bool, queue_size=10, tcp_nodelay=True)   #Seleciona área scanner 4
pub_sel_scanner_3 = rospy.Publisher("agv_p52", Bool, queue_size=10, tcp_nodelay=True)   #Seleciona área scanner 3
pub_sel_scanner_2 = rospy.Publisher("agv_p53", Bool, queue_size=10, tcp_nodelay=True)   #Seleciona área scanner 2
pub_sel_scanner_1 = rospy.Publisher("agv_p54", Bool, queue_size=10, tcp_nodelay=True)   #Seleciona área scanner 1

pub_acelerador = rospy.Publisher("G1EA1800CV1_velocidade", Int16, queue_size=10, tcp_nodelay=True) #Controle de velocidade
 

#Variaveis ----------------------------------------------------------------------------------------------------
#Estado
estadoAtual = "Iniciando"   #Estado atual do AGV
rotaAtual = 0               #Rota atual do AGV

#Função
funcao = False              #Se está executando uma função no momento

#Carregador
modo_carregador = False     #Indica se está no modo carregador
interlock = False           #Indica se o interlock foi acionado
liga_agv = False            #Para liga durante modo_carregador

#Emergência
emergencia = False          #Indica se entrou em emergência (uma vez em emergência, só volta ao normal ao reiniciar)
emergencia_remota = False   #Indica se entrou em "emergência remota" (nome não tecnicamente certo)

#Manual
manual = False                  #Indica se está em modo manual
modo_cadastro = False           #Para entrar no modo cadastro de pontos

#Parado
liberado = False            #Indica se o AGV está liberado para rodar
parado_cruzamento = False   #Indica se o AGV está parado por cruzamento
parado_automatico = False   #Indica se o AGV está parado pelo supervisório
parado_tag = False          #Indica se o AGV está parado por função de ponto/tag
intervencao_stop = True     #Indica se o AGV está parado por intervenção no botão (estado logo após o iniciando, começa em True)
token_botao = True          #Indica se o botão de start/stop deve fazer alguma função, de acordo com o estado
home = False                #Indica se o AGV está na posição "HOME"
botao_antigo = False        #Estado antigo do botão start/stop, para debounce

#Scanner
tipo_scanner = 1                            #Tipo atual do scanner, indica quando acontece parada por obstáculo: 0 - Apenas área interna; 1 - Área Intermediária; 2 - Área Externa 
                                            #Pelo funcionamento normal, no tipo 0, as áreas externa e intermediária ocasionam redução de velocidade
obstaculo_scanner1_externo = False          #Indica se há obstáculo na área externa do scanner 1
obstaculo_scanner1_intermediario = False    #Indica se há obstáculo na área intermediária do scanner 1
obstaculo_scanner1_interno = False          #Indica se há obstáculo na área interna do scanner 1
obstaculo_scanner1 = False                  #Indica se está parado por obstáculo pelo scanner 1 (requer que haja obstáculo por determinado tempo na área)
obstaculo_scanner2_externo = False          #Indica se há obstáculo na área externa do scanner 2
obstaculo_scanner2_intermediario = False    #Indica se há obstáculo na área intermediária do scanner 2
obstaculo_scanner2_interno = False          #Indica se há obstáculo na área interna do scanner 2
obstaculo_scanner2 = False                  #Indica se está parado por obstáculo pelo scanner 2 (requer que haja obstáculo por determinado tempo na área)
scanner_especial = False                    #Para a função de coleta

#Bateria
bateria_critica = False     #Indica se está com bateria crítica

#Navegacao
fuga = False        #Indica se aconteceu fuga de rota
joystick = False    #Indica se está no modo Joystick
        
#Buzina & Buzzer
#buzzer = False      #Indica se está buzinando (buzzer)
#buzinando = False   #Indica se deve parar de buzinar (buzzer)
buzzOn = False      #Para buzinar
buzina = 0          #Quantidade de vezes para buzinar
buzina_continua = False #Se deve buzinar continuamente


#Parâmetros
try:
    CENTRO_DIRECAO = Database.getItem("ConfigPaleteira", "Item", "CENTRO_DIRECAO")[0][1]    #Valor do centro da direção
except:
    CENTRO_DIRECAO = 127    #Como base, usa 127 (metade do valor máximo)
    print("Centro direcao nao encontrado no BD")

try:
    velocidade_lenta = Database.getItem("ConfigPaleteira", "Item", "VELOCIDADE_LENTA")[0][1]
except:
    velocidade_lenta = 30

try:
    velInicial = Database.getAllItems("Configuracao")[0][5] #Valor da velocidade inicial (para ser buscada no banco de dados)
except:
    velInicial = 1  #Como base, usa 1 (busca no banco de dados qual a velocidade indica pela posição 1)

try:
    scannInicial = Database.getAllItems("Configuracao")[0][4] #Valor do scanner atual (para ser buscado no banco de dados)
except:
    scannInicial = 1 #Como base, usa 1 (busca no banco de dados qual combinação de entradas é o scanner 1)

#Reseta tabela de rotas para ter apenas a rota inicial
try:
    tabelaRotas = Database.getAllItems("Rotas")[0][1:]          #Tabela (vetor) contendo as rotas
    rotaInicial = Database.getAllItems("Configuracao")[0][1]    #Valor da rota inicial
    cont_rota = 1
    for item in tabelaRotas:
        if(cont_rota < 11):
            name = "Rota"+str(cont_rota)
            Database.updateItem("Rotas", name, str(rotaInicial), "id", "1")
            cont_rota += 1
except:
    rotaInicial = 1 #Como base, usa a rota 1


#Erros
erro_comunicacao = False    #Indica se ocorreu erro de comunicação
erro_encoder = False        #Indica se ocorreu erro pelo encoder de navegação (AGV deveria andar mas está parado)
erro_carregador = False     #Indica se ocorreu erro relacionado ao carregador 
erro_encoderDirecao = False #Indica se ocorreu erro relacionado ao encoder de direção
erro_pose = False           #Indica se o scanner & hector_mapping não estão funcionando corretamente
erro_zeramento = False      #Indica se houve erro ao zerar o erro
sincronizando = False       #Indica se perdeu a comunicação com o supervisório
falha_plataforma = False    #Indica se houve falha ao atuar na plataforma
erro_freio = False          #Indica se houve falha ao acionar o freio

reset_zera_erro = False     #Indica se deve tentar zerar o erro novamente

#Contadores
con_entradas = 0            #Contador para a entrada, pode gerar Falha de Comunicacao
con_encoder = 0             #Contador para o encoder, pode gerar Falha de Encoder
con_tartaruga = 0           #Contador para o modo tartaruga (vel seg), usado para "resetar" o modo depois um tempo acionado
con_encoderDirecao = 0      #Contador para o encoder de direção, pode gerar Falha Encoder Direcao
con_bateria = 0             #Contador para a bateria, pode gerar Bateria Baixa
con_sc1 = 0                 #Contador para sair da parada por scanner 1
con_sc2 = 0                 #Contador para sair da parada por scanner 2
con_joy = 0                 #Contador para o modo joystick, faz sair desse modo
con_reducao = 0             #Contador para parar de reduzir a velocidade
con_carregador = 0          #Contador para a temporização para sair do carregador
con_desliga_agv = 0         #Contador para a temporização para desligar AGV no carregador
con_manual = 20             #Contador para acionar modo manual
con_auto = 0                #Contador para acionar modo automatico
con_obs = 0                 #Contador para os obstáculos (impedir que fique oscilando)
con_init = 100              #Para não iniciar em erro (por exemplo, se estiver em manual)
con_pose = 0                #Para verificar se o scanner ligou corretamente
con_emer = 0                #Para entrar em emergencia (debounce)
btn_cnt = 0                 #Para debounce do botão de start/stop
#con_buzzer_obs = 0          #Para buzinar se muito tempo parado por obstaculo (buzzer)
con_buzina = 0              #Para buzinar
con_buzina_scanner = 0      #Para buzinar por obstáculo
rst_cnt = 0                 #Para resetar mapa ao pressionar botão


#------------------------------------------------------ CALLBACKS -----------------------------------------------------#

#Desliga Temporizado
def agv_p13_callback(data):
    if(data.data < 600):
        estadoAtual = "Desligado"
        pub_estado.publish(estadoAtual)
        sudo_password = 'AGVS2016'
        command = 'shutdown -h now'.split()
        p = Popen(['sudo', '-S'] + command, stdin=PIPE, stderr=PIPE, universal_newlines=True)
        sudo_prompt = p.communicate(sudo_password + '\n')[1]

#Encoder Garfo
def agv_p20_callback(data):
    pass

#Start/Stop
def agv_p28_callback(data):
    global botao_antigo, token_botao, modo_carregador, liberado, intervencao_stop, parado_automatico, parado_cruzamento, parado_tag, home
    global con_init, liga_agv, btn_cnt, buzzer, con_buzzer_obs, con_auto, fuga, erro_zeramento, rst_cnt
    if(data.data == False and estadoAtual == "Manual"):
        if(rst_cnt < 75):
            rst_cnt = rst_cnt + 1
        else:
            rst_cnt = 0
            pub_syscommand.publish("reset")
            pub_reset_navegacao.publish(True)
            pub_pisca_feedback.publish(True)
            pub_acao.publish(57)
            pub_pid.publish(1)
    else:
        rst_cnt = 0
        
    if(data.data == True):
        botao_antigo = True
        btn_cnt = 0
    else:
        if(token_botao):
            #print("Token botao validado")
            if(btn_cnt < 2):
                btn_cnt += 1
            if(botao_antigo == True and btn_cnt == 2):
                botao_antigo = False
                #con_buzzer_obs = 0
                #buzzer = False
                resetaErro_encoder()
                if(modo_carregador == True and interlock == True):
                    pub_desacoplar.publish(True)
                elif(modo_carregador == True and interlock == False):
                    con_init = 100
                    liberado = True
                    liga_agv = True
                    modo_carregador = False
                elif(modo_carregador == False and interlock == True):
                    pass
                else:
                    liberado = not liberado
                    print("Botao pressionado")
                    if(estadoAtual == "Falha de Referencia" or estadoAtual == "Fuga de Rota"):
                        fuga = False
                        erro_zeramento = False
                        pub_reset_navegacao.publish(True)
                    if(not liberado):
                        intervencao_stop = True
                        pub_trocaVelocidade.publish(velInicial)
                    else:
                        con_auto = 20
                        intervencao_stop = False
                        parado_automatico = False
                        parado_cruzamento = False
                        parado_tag = False
                        home = False
        else:
            botao_antigo = False

#Interlock
def agv_p29_callback(data): 
    global interlock
    if(data.data == True):
        interlock = True
        pub_interlock.publish(interlock)
    else:
        interlock = False
        pub_interlock.publish(interlock)

#Sinal Freio pressionado
def agv_p30_callback(data):
    pass
    
#Controle Manual Direita
def agv_p31_callback(data):
    pass
    
#Controle Manual Esquerda
def agv_p32_callback(data):
    pass

#Sinal Manual/Automático
def agv_p33_callback(data):
    global manual
    resetaErro_comunicacao()
    if(data.data == True):
        manual = False
    else:
        manual = True
        parado_automatico = False

#Sinal Emergência
def agv_p34_callback(data):
    global emergencia, con_emer, init_equip
    init_equip = True
    if(data.data == True):
        if(con_emer < 2):
            con_emer += 1
        if(con_emer >= 2):
            emergencia = True
    else:
        emergencia = False
        con_emer = 0


#Encoder Locomoção Roda Direita ~ Interrupção na placa
def agv_p35_callback(data):
    pass

#Encoder Locomoção Roda Esquerda ~ Interrupção na placa
def agv_p36_callback(data):
    pass

#Encoder Bomba Hidráulica ~ Interrupção na placa
def agv_p37_callback(data):
    pass

#Sinal Ultrassônico
def agv_p38_callback(data):
    pass
    
#Scanner Externo 2
def agv_p39_callback(data):
    #pass
    global obstaculo_scanner2_externo
    if(data.data == True):
        obstaculo_scanner2_externo = True
    else:
        obstaculo_scanner2_externo = False
        
#Scanner Intermediário 2
def agv_p40_callback(data):
    #pass
    global obstaculo_scanner2_intermediario
    if(data.data == True):
        obstaculo_scanner2_intermediario = True
    else:
        obstaculo_scanner2_intermediario = False
        
#Scanner Interno 2
def agv_p41_callback(data):
    #pass
    global obstaculo_scanner2_interno
    if(data.data == True):
        obstaculo_scanner2_interno = True
    else:
        obstaculo_scanner2_interno = False


def output_paths_callback(data):
    global obstaculo_scanner1_externo, obstaculo_scanner1_intermediario, obstaculo_scanner1_interno
    
    if(data.status[0] == False):
        obstaculo_scanner1_externo = True
    else:
        obstaculo_scanner1_externo = False
    
    if(data.status[1] == False):
        obstaculo_scanner1_intermediario = True
    else:
        obstaculo_scanner1_intermediario = False
    
    if(data.status[2] == False):
        obstaculo_scanner1_interno = True
    else:
        obstaculo_scanner1_interno = False

'''
#Scanner Externo 1
def agv_p42_callback(data):
    global obstaculo_scanner1_externo
    if(data.data == True):
        obstaculo_scanner1_externo = True
    else:
        obstaculo_scanner1_externo = False 

#Scanner Intermediário 1
def agv_p43_callback(data):
    global obstaculo_scanner1_intermediario
    if(data.data == True):
        obstaculo_scanner1_intermediario = True
    else:
        obstaculo_scanner1_intermediario = False        
        
#Scanner Interno 1
def agv_p44_callback(data):
    global obstaculo_scanner1_interno
    if(data.data == True):
        obstaculo_scanner1_interno = True
    else:
        obstaculo_scanner1_interno = False
'''


#---------------------------------------------------------------------------------------------

def fuga_callback(data):
    global fuga
    if(data.data == True):
        fuga = True
    else:
        fuga = False
        
def erropos_callback(data):
    global erro_zeramento
    if(data.data == True):
        erro_zeramento = True
    else:
        erro_zeramento = False
        
def erroplataforma_callback(data):
    global falha_plataforma
    if(data.data == True):
        falha_plataforma = True
    else:
        falha_plataforma = False
           
def joy_callback(joy):
    global joystick
    global estadoAtual
    con_joy = 0
    joystick = True
    if(estadoAtual == "Controle Remoto"):
        pub_acelerador.publish(round(joy.linear.x))
        pub_direcao.publish(round(joy.angular.z))

    
def encoder_callback(data):
    global con_encoder
    if(estadoAtual == "Rodando"):
        if(data.data != 0):
            con_encoder = 0


def pose_callback(data):
    global con_pose, erro_pose
    con_pose = 0
    erro_pose = False
    
def areas_mod_callback(data):
    global tipo_scanner
    tipo_scanner = data.data

        
def bateria_callback(bateria):
    global bateria_critica
    global con_bateria
    try:
        critical = Database.getAllItems("Configuracao")[0][3]
    except:
        critical = 20000
    if (bateria.data > critical):
        bateria_critica = False
        con_bateria = 0
    else:
        pass
        #con_bateria+=1
        #if(con_bateria > 10):
        #    bateria_critica = True

def fim_carregar_callback(data):
    global modo_carregador, con_carregador, liga_agv, funcao
    if(modo_carregador == True and con_carregador == 0):
        con_carregador = 10 #10 segundos
        liga_agv = True
        print("Tentando ligar o agv...")

def encoder_dist_callback(data):
    global distancia_encoder
    distancia_encoder = data.data
    
def fim_funcao_callback(data):
    global funcao, tipo_scanner, scanner_atual, buzzer, buzinando
    funcao = False
    #tipo_scanner = 0
    #buzzer = False
    #buzinando = False
    
def cadastroPonto_callback(data):
    global modo_cadastro
    if(data.data == True):
        modo_cadastro = True
    else:
        modo_cadastro = False
    
def rota_callback(data):
    global rotaAtual
    rotaAtual = data.data

def funcao_callback(data):
    global funcao
    funcao = data.data

def quase_coleta_callback(data):
    global quase_coleta, con_init, liberado, liga_agv, modo_carregador
    quase_coleta = data.data
    
    if(quase_coleta == True and modo_carregador == True and interlock == True):
        pub_desacoplar.publish(True)
    
    elif(quase_coleta == True and modo_carregador == True and interlock == False):
        con_init = 100
        liberado = True
        liga_agv = True
        modo_carregador = False

def quase_entrega_callback(data):
    global quase_entrega, con_init, liberado, liga_agv, modo_carregador
    quase_entrega = data.data
    
    if(quase_entrega == True and modo_carregador == True and interlock == True):
        pub_desacoplar.publish(True)
    
    elif(quase_entrega == True and modo_carregador == True and interlock == False):
        con_init = 100
        liberado = True
        liga_agv = True
        modo_carregador = False
        
def parada_remota_callback(data):
    global emergencia_remota
    emergencia_remota = data.data
           
def acao_callback(acao):
    global liberado
    global parado_automatico
    global parado_cruzamento
    global parado_tag
    global intervencao_stop
    global home
    global erro_encoder
    global modo_carregador
    global buzina, buzinando, buzina_continua
    global emergencia_remota
    global freq_atual, buzzer
    global con_desliga_agv, scanner_atual, tipo_scanner, liga_agv
    
    print("Acao recebida: " + str(acao.data))
    
    if(acao.data == 1): #Play
        if(modo_carregador == False):
            liberado = True
            parado_cruzamento = False
            parado_automatico = False
            intervencao_stop = False
            parado_tag = False
            home = False
            erro_encoder = False
        else:
            pub_desacoplar.publish(True)
    elif(acao.data == 2): #Stop Automatico
        liberado = False
        parado_automatico = True
    elif(acao.data == 3): #Velocidade 1
        pub_trocaVelocidade.publish(1)
    elif(acao.data == 4): #Velocidade 2
        pub_trocaVelocidade.publish(2)
    elif(acao.data == 5): #Velocidade 3
        pub_trocaVelocidade.publish(3)
    elif(acao.data == 6): #Velocidade 4
        pub_trocaVelocidade.publish(4)
    elif(acao.data == 7): #Velocidade 5
        pub_trocaVelocidade.publish(5)
    elif(acao.data == 8): #Velocidade 6
        pub_trocaVelocidade.publish(6)
    elif(acao.data == 9): #Velocidade 7
        pub_trocaVelocidade.publish(7)
    elif(acao.data == 10): #Velocidade 8
        pub_trocaVelocidade.publish(8)
    elif(acao.data == 11): #Velocidade 9
        pub_trocaVelocidade.publish(9)
    elif(acao.data == 12): #Velocidade 10
        pub_trocaVelocidade.publish(10)
    elif(acao.data == 13): #Buzinar
        buzina = Database.getAllItems("Configuracao")[0][7]
    elif(acao.data == 14): #Area Scanner 1
        gerenciaScanner(Database.getItem("Scanner", "id", "1")[0])
        scanner_atual = 1
    elif(acao.data == 15): #Area Scanner 2
        gerenciaScanner(Database.getItem("Scanner", "id", "2")[0])
        scanner_atual = 2
    elif(acao.data == 16): #Area Scanner 3
        gerenciaScanner(Database.getItem("Scanner", "id", "3")[0])
        scanner_atual = 3
    elif(acao.data == 17): #Area Scanner 4
        gerenciaScanner(Database.getItem("Scanner", "id", "4")[0])
        scanner_atual = 4
    elif(acao.data == 18): #Area Scanner 5
        gerenciaScanner(Database.getItem("Scanner", "id", "5")[0])
        scanner_atual = 5
    elif(acao.data == 19): #Area Scanner 6
        gerenciaScanner(Database.getItem("Scanner", "id", "6")[0])
        scanner_atual = 6
    elif(acao.data == 20): #Area Scanner 7
        gerenciaScanner(Database.getItem("Scanner", "id", "7")[0])
        scanner_atual = 7
    elif(acao.data == 21): #Area Scanner 8
        gerenciaScanner(Database.getItem("Scanner", "id", "8")[0])
        scanner_atual = 8
    elif(acao.data == 22): #Area Scanner 9
        gerenciaScanner(Database.getItem("Scanner", "id", "9")[0])
        scanner_atual = 9
    elif(acao.data == 23): #Area Scanner 10
        gerenciaScanner(Database.getItem("Scanner", "id", "10")[0])
        scanner_atual = 10
    elif(acao.data == 24): #Area Scanner 11
        gerenciaScanner(Database.getItem("Scanner", "id", "11")[0])
        scanner_atual = 11
    elif(acao.data == 25): #Area Scanner 12
        gerenciaScanner(Database.getItem("Scanner", "id", "12")[0])
        scanner_atual = 12
    elif(acao.data == 26): #Area Scanner 13
        gerenciaScanner(Database.getItem("Scanner", "id", "13")[0])
        scanner_atual = 13
    elif(acao.data == 27): #Area Scanner 14
        gerenciaScanner(Database.getItem("Scanner", "id", "14")[0])
        scanner_atual = 14
    elif(acao.data == 28): #Area Scanner 15
        gerenciaScanner(Database.getItem("Scanner", "id", "15")[0])
        scanner_atual = 15
    elif(acao.data == 29): #Area Scanner 16
        gerenciaScanner(Database.getItem("Scanner", "id", "16")[0])
        scanner_atual = 16
    elif(acao.data == 30): #Frequencia 1
        pub_trocar_rota.publish(1)
        #pub_sel_freq.publish(False)
        #freq_atual = 0
    elif(acao.data == 31): #Frequencia 2
        pub_trocar_rota.publish(2)
        #pub_sel_freq.publish(True)
        #freq_atual = 1
    elif(acao.data == 32): #Modo carregar bateria
        pub_acelerador.publish(0)
        con_desliga_agv = 50
        modo_carregador = True
        liberado = False
        parado_cruzamento = False
        parado_automatico = False
        intervencao_stop = False
        parado_tag = False       
    elif(acao.data == 33): #AGV Home
        liberado = False
        home = True
    elif(acao.data == 34): #Pular Rota
        troca_rota()
        
    elif(acao.data == 35): #Stop Manual
        liberado = False
        
    elif(acao.data == 36): #Stop Tag
        liberado = False
        parado_tag = True
        
    elif(acao.data == 37): #Stop Cruzamento
        liberado = False
        parado_cruzamento = True
        
    elif(acao.data == 38): #Emergencia remota
        emergencia_remota = True
        liberado = False
        parado_automatico = True #Trata como parada automática
    
    elif(acao.data == 39): #Controle remoto????
        pass
    
    elif(acao.data == 40): #Velocidade Seg -- Não usa na paleteira
        pass
    
    elif(acao.data == 41): #Velocidade 11
        pub_trocaVelocidade.publish(11)
    elif(acao.data == 42): #Velocidade 12
        pub_trocaVelocidade.publish(12)
    elif(acao.data == 43): #Velocidade 13
        pub_trocaVelocidade.publish(13)
    elif(acao.data == 44): #Velocidade 14
        pub_trocaVelocidade.publish(14)
    elif(acao.data == 45): #Velocidade 15
        pub_trocaVelocidade.publish(15)
    elif(acao.data == 46): #Reset encoder
        pub_encoderReset.publish(True)
    elif(acao.data == 53):  #Ativar buzina contínua
        buzina_continua = True
    #    buzzer = True
    #    buzinando = True
    elif(acao.data == 54):  #Desligar buzina contínua
        buzina_continua = False
    #    buzzer = False
    #    buzinando = False
    elif(acao.data == 56): #Ré
        pub_frente.publish(False)
    elif(acao.data == 57): #Frente (sentido garfo)
        pub_frente.publish(True)
    elif(acao.data == 58): #PID 1
        pub_pid.publish(1)
    elif(acao.data == 59): #PID 2
        pub_pid.publish(2)
    elif(acao.data == 60): #PID 3
        pub_pid.publish(3)
    elif(acao.data == 61): #PID 4
        pub_pid.publish(4)
        
    elif(acao.data == 62): #Garfo 1
        altura_garfo = Database.getItem("Garfo", "id", "1")[0][1]
        print("Setting altura garfo: " + str(altura_garfo))
        pub_garfo.publish(int(altura_garfo))
    elif(acao.data == 63): #Garfo 2
        altura_garfo = Database.getItem("Garfo", "id", "2")[0][1]
        print("Setting altura garfo: " + str(altura_garfo))
        pub_garfo.publish(int(altura_garfo))
    elif(acao.data == 64): #Garfo 3
        altura_garfo = Database.getItem("Garfo", "id", "3")[0][1]
        print("Setting altura garfo: " + str(altura_garfo))
        pub_garfo.publish(int(altura_garfo))
    elif(acao.data == 65): #Garfo 4
        altura_garfo = Database.getItem("Garfo", "id", "4")[0][1]
        print("Setting altura garfo: " + str(altura_garfo))
        pub_garfo.publish(int(altura_garfo))
    elif(acao.data == 66): #Garfo 5
        altura_garfo = Database.getItem("Garfo", "id", "5")[0][1]
        print("Setting altura garfo: " + str(altura_garfo))
        pub_garfo.publish(int(altura_garfo))
    elif(acao.data == 67): #Garfo 6
        altura_garfo = Database.getItem("Garfo", "id", "6")[0][1]
        print("Setting altura garfo: " + str(altura_garfo))
        pub_garfo.publish(int(altura_garfo))
    elif(acao.data == 68): #Garfo 7
        altura_garfo = Database.getItem("Garfo", "id", "7")[0][1]
        print("Setting altura garfo: " + str(altura_garfo))
        pub_garfo.publish(int(altura_garfo))
    elif(acao.data == 69): #Garfo 8
        altura_garfo = Database.getItem("Garfo", "id", "8")[0][1]
        print("Setting altura garfo: " + str(altura_garfo))
        pub_garfo.publish(int(altura_garfo))
    elif(acao.data == 70): #Garfo 9
        altura_garfo = Database.getItem("Garfo", "id", "9")[0][1]
        print("Setting altura garfo: " + str(altura_garfo))
        pub_garfo.publish(int(altura_garfo))
    elif(acao.data == 71): #Garfo 10
        altura_garfo = Database.getItem("Garfo", "id", "10")[0][1]
        print("Setting altura garfo: " + str(altura_garfo))
        pub_garfo.publish(int(altura_garfo))
    elif(acao.data == 72): #Verifica garfo
        pub_verifica_garfo.publish(True)
    
        
#-------------------------------------------------------------------------------------------------

def troca_rota():
    dados = Database.getAllItems("Rotas")[0][1:]
    rotaInicial = Database.getAllItems("Configuracao")[0][1]

    cont = 1
    for item in dados:
        if(cont < 10):
            name = "Rota"+str(cont)
            #print(name)
            #print(dados[cont])
            Database.updateItem("Rotas", name, str(dados[cont]), "id", "1")
            #Database.closeConn()
            cont += 1
        
    Database.updateItem("Rotas", "Rota10", str(rotaInicial), "id", "1")
        

def gerenciaBuzina():
    global buzzOn
    global buzina
    global con_buzina
    con_buzina += 1
    if con_buzina == 2 and not buzzOn:
        #print("Buzina on")
        #pub_buzina.publish(True)
        buzzOn = True
        con_buzina = 0
    elif con_buzina == 2 and buzzOn:
        #print("Buzina off")
        #pub_buzina.publish(False)
        buzzOn = False
        con_buzina = 0
        buzina -= 1

def gerenciaScanner(values):
    print("Enviando scanner: " + str(values))
    if(values[1]):
        pub_sel_scanner_1.publish(True)
    else:
        pub_sel_scanner_1.publish(False)
    if(values[2]):
        pub_sel_scanner_2.publish(True)
    else:
        pub_sel_scanner_2.publish(False) 
    if(values[3]):
        pub_sel_scanner_3.publish(True)
    else:
        pub_sel_scanner_3.publish(False)
    if(values[4]):
        pub_sel_scanner_4.publish(True)
    else:
        pub_sel_scanner_4.publish(False)


def resetaErro_comunicacao():
    global erro_comunicacao
    global con_entradas
    
    erro_comunicacao = False
    con_entradas = 0

def resetaErro_encoder():
    global erro_encoder
    global con_encoder
    
    erro_encoder = False
    con_encoder = 0

def resetaErro_encoderDirecao():
    global erro_encoderDirecao
    global con_encoderDirecao
    
    erro_encoderDirecao = 0
    con_encoderDirecao = 0
    
init_equip = False
inited_equip = False
#Faz a inicializacao apos receber os primeiros dados da central
def init_agv():
    global init_equip, inited_equip
    if(init_equip == True and inited_equip == False): #Se já recebeu dados da central e ainda não inicializou
        gerenciaScanner(Database.getItem("Scanner", "id", str(scannInicial))[0]) #Aplica o scanner inicial
        pub_trocaVelocidade.publish(int(velInicial))    #Aplica a velocidade inicial
        inited_equip = True #Só realiza a inicialização uma vez
      
def logica_scanner():
    global obstaculo_scanner1_interno, obstaculo_scanner2_interno, obstaculo_scanner2_intermediario, obstaculo_scanner1_externo, obstaculo_scanner2_externo
    global obstaculo_scanner1, obstaculo_scanner2, con_sc1, con_sc2, liberado, parado_automatico
    global con_obs, tipo_scanner, scanner_especial, con_reducao
    
    #tipo_scanner
    #1 - Interna para, externa e intermediaria reduzem
    #2 - Interna, intermediaria e externa param
    #3 - Interna e intermediaria param, externa reduz
    #4 - Interna para, ignora externa e intermediaria
    
    
    if(obstaculo_scanner1_interno == True):       
        if(con_obs < 3):
            con_obs += 1
        if(con_obs == 3):
            obstaculo_scanner1 = True
            con_sc1 = 10
    elif(obstaculo_scanner2_interno == True):
        if(con_obs < 3):
            con_obs += 1
        if(con_obs == 3):
            obstaculo_scanner2 = True
            con_sc2 = 10
    else:
        con_obs = 0
        
    #Ignora áreas externa e intermediária
    if(tipo_scanner == 4):
        return
               
    if(obstaculo_scanner2_intermediario == True): #and (tipo_scanner < 4)):
        if(tipo_scanner == 2 or tipo_scanner == 3):
            obstaculo_scanner2 = True
            con_sc2 = 10
        else:
            con_reducao = 10
    if(obstaculo_scanner1_intermediario == True):
        if(tipo_scanner == 2 or tipo_scanner == 3):
            obstaculo_scanner1 = True
            con_sc1 = 10
        else:
            con_reducao = 10
    elif(obstaculo_scanner1_externo == True):
        if(tipo_scanner == 2):
            obstaculo_scanner1 = True
            con_sc1 = 10
            #print("Obstaculo scanner 1 externo!!")
        else:
            con_reducao = 10
    elif(obstaculo_scanner2_externo == True):
        #print("OS 2 externo -- Tipo scanner: " + str(tipo_scanner))
        if(scanner_especial == True and tipo_scanner == 2):
            obstaculo_scanner2 = True
            con_sc2 = 10
            #print("Obstaculo scanner 2 externo!!")
        else:
            con_reducao = 10
    
def executa_manual():
    global con_auto, tipo_scanner
    con_auto = 20   
    pub_acelerador.publish(0)  
    tipo_scanner = 1

def standby():
    global con_auto, con_manual
    pub_standby.publish(True)
    pub_acelerador.publish(0)
    con_auto = 20
    con_manual = 20

    
def executa_automatico():
    global con_auto, con_manual
    con_manual = 20
    if(con_auto > 0):
        con_auto -= 1
        

            

if __name__ == '__main__':
    rospy.init_node('Estados', anonymous=False)
    rospy.Subscriber("agv_p20", Int16, agv_p20_callback, queue_size=1, buff_size=2**24) 
    rospy.Subscriber("agv_p28", Bool, agv_p28_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("agv_p29", Bool, agv_p29_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("agv_p30", Bool, agv_p30_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("agv_p31", Bool, agv_p31_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("agv_p32", Bool, agv_p32_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("agv_p33", Bool, agv_p33_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("agv_p34", Bool, agv_p34_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("agv_p35", Bool, agv_p35_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("agv_p36", Bool, agv_p36_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("agv_p37", Bool, agv_p37_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("agv_p38", Bool, agv_p38_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("agv_p39", Bool, agv_p39_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("agv_p40", Bool, agv_p40_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("agv_p41", Bool, agv_p41_callback, queue_size=1, buff_size=2**24)
    
    rospy.Subscriber("/sick_safetyscanners/output_paths", OutputPathsMsg, output_paths_callback, queue_size=1, buff_size=2**24)
    #Substituídos por /sick_safetyscanners/output_paths
    #rospy.Subscriber("agv_p42", Bool, agv_p42_callback, queue_size=1, buff_size=2**24)
    #rospy.Subscriber("agv_p43", Bool, agv_p43_callback, queue_size=1, buff_size=2**24)
    #rospy.Subscriber("agv_p44", Bool, agv_p44_callback, queue_size=1, buff_size=2**24)
    
    
    rospy.Subscriber("/poseupdate", PoseWithCovarianceStamped, pose_callback, queue_size=10, buff_size=2**24)
    rospy.Subscriber("cmd_vel_joy", Twist, joy_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("acao", Int16, acao_callback, queue_size=10, buff_size=2**24)
    rospy.Subscriber("agv_encoder", Float32, encoder_callback, queue_size=1, buff_size=2**24) #Velocidade baseada no encoder
    rospy.Subscriber("agv_encoder_dist_count", UInt32, encoder_dist_callback, queue_size=1, buff_size=2**24) #Distancia baseada no encoder 
    rospy.Subscriber("bateria", Float64, bateria_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("fim_carregar", Bool, fim_carregar_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("fim_funcao", Bool, fim_funcao_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("rota_atual", Int16, rota_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("inicio_funcao", Bool, funcao_callback, queue_size=1, buff_size=2**24)
    
    rospy.Subscriber("fuga_rota", Bool, fuga_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("erro_pos", Bool, erropos_callback, queue_size=1, buff_size=2**24)
    rospy.Subscriber("erro_plataforma", Bool, erroplataforma_callback, queue_size=1, buff_size=2**24)
    
    rospy.Subscriber("areas_mod", Int16, areas_mod_callback, queue_size=1, buff_size=2*24)
    
    rospy.Subscriber("cadastro_ponto", Bool, cadastroPonto_callback, queue_size=1, buff_size=2**24)

    rospy.Subscriber("parada_remota", Bool, parada_remota_callback, queue_size=1, buff_size=2**24)

    
    estadoAtual = "Iniciando"
    pub_estado.publish(estadoAtual)
      
    #Velocidade Inicial
    #pub_trocaVelocidade.publish(int(velInicial))
    

    rate = rospy.Rate(10) # 10hz --> 1 vez a cada 100ms
    while not rospy.is_shutdown():
    
        #Define estado atual
        if(emergencia == True):
            estadoAtual = "Emergencia"
            standby()
            funcao = False
            token_botao = False
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
            
        #------------------------------------------------------------------------------------
        elif(emergencia_remota == True):
            estadoAtual = "Emergencia Remota"
            standby()
            funcao = False
            token_botao = False
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)

        #------------------------------------------------------------------------------------
        elif(erro_comunicacao == True):
            estadoAtual = "Falha Comunicacao"
            standby()
            funcao = False
            token_botao = False
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)

        #------------------------------------------------------------------------------------
        elif(con_init > 0):
            estadoAtual = "Iniciando"
            standby()
            funcao = False
            #pub_direcao.publish(CENTRO_DIRECAO)
            token_botao = False
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
            con_init -= 1
        #------------------------------------------------------------------------------------
        #elif(forca_teste == True):
        #    estadoAtual = "Teste" 
        #------------------------------------------------------------------------------------
        elif(erro_pose == True):
            estadoAtual = "Falha Conexao Scanner" #Falha no hector_mapping ou no sick_safetyscanners
            standby()
            funcao = False
            token_botao = False
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
        #------------------------------------------------------------------------------------
        #elif(falha_scanner_1 == True):
        #    estadoAtual = "Falha Scanner 1"
        #    standby()
        #    funcao = False
        #    token_botao = False
        #    pub_acoplar.publish(False)
        #    pub_desacoplar.publish(False)
        #------------------------------------------------------------------------------------
        #elif(falha_scanner_2 == True):
        #    estadoAtual = "Falha Scanner 2"
        #    standby()
        #    funcao = False
        #    token_botao = False
        #    pub_acoplar.publish(False)
        #    pub_desacoplar.publish(False)
        #------------------------------------------------------------------------------------
        elif(erro_freio == True):
            estadoAtual = "Falha Freio"
            standby()
            funcao = False
            token_botao = False
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
        #------------------------------------------------------------------------------------
        #elif(erro_rfid == True):
        #    estadoAtual = "Falha RFID"
        #    standby()
        #    funcao = False
        #    pub_acelerador.publish(0)
        #    token_botao = False
        #    pub_acoplar.publish(False)
        #    pub_desacoplar.publish(False)
        #------------------------------------------------------------------------------------
        elif(interlock == True and manual == True):
            estadoAtual = "Sinal Interlock"
            #pub_aciona_equip.publish(True)
            standby()
            #funcao = False
            token_botao = False
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
        #------------------------------------------------------------------------------------
        elif(modo_carregador == True):
            estadoAtual = "Carregando"
            standby()
            pub_acoplar.publish(True)
            if(liga_agv):
                #pub_aciona_equip.publish(False)
                print("Ligando agv...")
            else:
                pass
                #pub_aciona_equip.publish(True)
            token_botao = True
            
            if(manual == True and interlock == False):
                modo_carregador = False
                con_init = 100
        #------------------------------------------------------------------------------------
        elif(bateria_critica == True):
            if(estadoAtual != "Bateria baixa"):
                gerenciaScanner(Database.getItem("Scanner", "id", str(scannInicial))[0])
                pub_trocaVelocidade.publish(velInicial)
            estadoAtual = "Bateria baixa"
            executa_manual()
            #buzzer = False
            troca_area = False
            liga_agv = False
            funcao = False
            token_botao = False
            intervencao_stop = True
            liberado = False
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
            
        #------------------------------------------------------------------------------------
        elif(modo_cadastro == True):
            estadoAtual = "Cadastro"
            #buzzer = False
            liga_agv = False
            executa_manual()
            intervencao_stop = True
            liberado = False
            funcao = False
            token_botao = False
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
            
        #------------------------------------------------------------------------------------     
        elif(manual == True):
            if(estadoAtual != "Manual"):
                gerenciaScanner(Database.getItem("Scanner", "id", str(scannInicial))[0])
                pub_trocaVelocidade.publish(velInicial)
            estadoAtual = "Manual"
            #buzzer = False
            liga_agv = False
            executa_manual()
            reset_zera_erro = True
            intervencao_stop = True
            liberado = False
            funcao = False
            token_botao = False
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
           
        #------------------------------------------------------------------------------------
        elif(falha_plataforma == True):
            estadoAtual = "Falha Plataforma"
            standby()
            funcao = False
            token_botao = False
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)

        #------------------------------------------------------------------------------------
        elif(joystick == True):
            estadoAtual = "Controle Remoto"
            funcao = False
            token_botao = False
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
        #------------------------------------------------------------------------------------
        elif(erro_encoder == True):
            estadoAtual = "Falha Encoder"
            liberado = False
            standby()
            funcao = False
            token_botao = True
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
        #------------------------------------------------------------------------------------
        elif(erro_encoderDirecao == True):
            estadoAtual = "Falha Encoder Direcao"
            liberado = False
            standby()
            funcao = False
            token_botao = True
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
            pub_desliga_equipamento.publish(False)
        #------------------------------------------------------------------------------------
        elif(parado_cruzamento == True): 
            estadoAtual = "Parado Cruzamento"
            standby()
            funcao = False
            token_botao = True
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
        #------------------------------------------------------------------------------------
        elif(parado_automatico == True): 
            estadoAtual = "Parada Automatica"
            standby()
            funcao = False
            token_botao = True
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
        #------------------------------------------------------------------------------------
        elif(home == True): 
            estadoAtual = "Home"
            standby()
            funcao = False
            token_botao = True
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
            #buz_parada_rodando = True
            #if(con_buzina_parado == 0):
            #    con_buzina_parado =  intervalo_buzina_tag #Buzina a cada intervalo de tempo
                
            #Para buzinar a cada intervalo de tempo quando parado em Home
            #if(con_buzina_parado > 0):
            #    con_buzina_parado -= 1
                #print("Contando: " + str(con_buzina_parado))
            #    if(con_buzina_parado == 0):
            #        buzina = buzina_por_tag
        #------------------------------------------------------------------------------------
        elif(parado_tag == True): 
            estadoAtual = "Parado Tag"
            standby()
            funcao = False
            token_botao = True
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
            #buz_parada_rodando = True
            #if(con_buzina_parado == 0):
            #    con_buzina_parado = intervalo_buzina_tag #Buzina a cada intervalo de tempo
                
 
            #Para buzinar a cada intervalo de tempo quando parado por tag
            #if(con_buzina_parado > 0):
            #    con_buzina_parado -= 1
                #print("Contando: " + str(con_buzina_parado))
            #    if(con_buzina_parado == 0):
            #        buzina = buzina_por_tag
        #------------------------------------------------------------------------------------
        elif(intervencao_stop == True): 
            estadoAtual = "Intervencao Stop"
            standby()
            #funcao = False
            token_botao = True
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
        #------------------------------------------------------------------------------------
        elif(erro_zeramento == True):
            estadoAtual = "Falha de Referencia"
            standby()
            funcao = False
            reset_zera_erro = True
            token_botao = True
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
        #------------------------------------------------------------------------------------
        elif(fuga == True and funcao == False):
            estadoAtual = "Fuga de Rota"
            standby()
            funcao = False
            reset_zera_erro = True
            token_botao = True
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
        #------------------------------------------------------------------------------------
        elif(obstaculo_scanner1 == True):
            estadoAtual = "Obstaculo SC1"
            #if(con_buzzer_obs < 150):
            #    con_buzzer_obs += 1
            #if(con_buzzer_obs >= 150):
            #    buzzer = True
            #con_sc1 = 30 #Para 3 segundos de contagem
            
            if(con_buzina_scanner == 0):
                con_buzina_scanner = 50 #Buzina a cada 5 segundos
                
            #Para buzinar a cada 5 segundos quando parado por scanner
            if(con_buzina_scanner > 0):
                con_buzina_scanner -= 1
                if(con_buzina_scanner == 0):
                    buzina = Database.getAllItems("Configuracao")[0][6]
            
            resetaErro_encoder()
            standby()
            token_botao = True
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
        #------------------------------------------------------------------------------------
        elif(obstaculo_scanner2 == True):
            estadoAtual = "Obstaculo SC2"
            #if(con_buzzer_obs < 150):
            #    con_buzzer_obs += 1
            #if(con_buzzer_obs >= 150):
            #    buzzer = True
            #con_sc2 = 30 #Para 3 segundos de contagem
            
            if(con_buzina_scanner == 0):
                con_buzina_scanner = 50 #Buzina a cada 5 segundos
                
            #Para buzinar a cada 5 segundos quando parado por scanner
            if(con_buzina_scanner > 0):
                con_buzina_scanner -= 1
                if(con_buzina_scanner == 0):
                    buzina = Database.getAllItems("Configuracao")[0][6]
            
            resetaErro_encoder()
            standby()
            token_botao = True
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
        #------------------------------------------------------------------------------------
        elif(funcao == True):
            if(con_auto == 0):
                estadoAtual = "Funcao"
            executa_automatico()
            #estadoAtual = "Funcao"
            token_botao = True
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)  
            #pub_aciona_luz.publish(True)
        #------------------------------------------------------------------------------------
        #elif(cadastro_tag == True):
        #    estadoAtual = "Cadastro Tag"
        #    token_botao = True
        #    executa_automatico()
        #    con_encoder += 1
        #    if(con_encoder > 90):
        #        erro_encoder = True
        #    pub_acoplar.publish(False)
        #    pub_desacoplar.publish(False)
        #------------------------------------------------------------------------------------
        # elif(natural == True):
            # estadoAtual = "Natural"
            # token_botao = True
            # pub_acoplar.publish(False)
            # pub_desacoplar.publish(False)
        #------------------------------------------------------------------------------------
        else:
            if(con_auto == 0):
                estadoAtual = "Rodando"
            elif(con_auto > 0 and reset_zera_erro == True):
                #pub_zera_erro.publish("-1")
                reset_zera_erro = False
                  
            token_botao = True
            executa_automatico()
            
            if(liga_agv == True):
                liga_agv = False
            
            #con_encoder += 1
            #if(con_encoder > 100 and con_auto == 0):
            #    erro_encoder = True
                #pub_hab_locomocao.publish(False) 
                #con_auto = 30
                #pub_aciona_luz.publish(False)
                #con_encoder = 0
            pub_acoplar.publish(False)
            pub_desacoplar.publish(False)
                
        #------------------------------------------------------------------------------------ 
        #Faz a inicializacao apos receber os primeiros dados da central
        init_agv()
        
        if(init_equip == True and estadoAtual != "Carregando" and estadoAtual != "Sinal Interlock" and interlock == False):
            #pub_aciona_equip.publish(False) #Aciona equipamento
            pass
        
        #Logica dos scanners
        logica_scanner()
        
        #Verifica se a tag atual faz buzinar em determinados intervalos de tempo
        #verifica_tag_buzina()
        
        con_joy += 1
        if(con_joy > 50):
            joystick = False
                    
        con_entradas += 1
        if(con_entradas > 20):
            erro_comunicacao = True
              
                        
        if(buzina > 0):
            gerenciaBuzina()
        else:
            con_buzina = 0
            if(buzina_continua == True):
                buzina = Database.getAllItems("Configuracao")[0][6]
        
        #Aciona ou desliga buzzer
        #if(buzzer == True):
        #    pub_buzzer.publish(True)
        #else:
        #    pub_buzzer.publish(False)
        

        #Reseta intervalo para buzinar por parada / Home
        #if(not(estadoAtual == "Parado Tag" or estadoAtual == "Home")):
            #print("Reseta buzina pois esta no estado: " + str(estadoAtual))
            #con_buzina_parado = intervalo_buzina_tag
         
        #Reseta intervalo para buzinar por scanner
        if(not(estadoAtual == "Obstaculo SC1" or estadoAtual == "Obstaculo SC2")):
            con_buzina_scanner = 1 #Para fazer buzinar no proximo loop
        #    con_buzzer_obs = 0
        #    if(buzinando == False):
        #        buzzer = False
        
        
        #if(not(estadoAtual == "Funcao" or "Obstaculo" in estadoAtual)):
        #    scanner_especial = False
        #    tipo_scanner = 0
            
        #Para sair do estado de obstaculo com 3 segundos depois de parar por scanner   
        if(con_sc1 > 0):
            #print("Obs Scanner 1: " + str(con_sc1))
            con_sc1 -= 1
            if(con_sc1 == 0):
                obstaculo_scanner1 = False
        if(con_sc2 > 0):
            #print("Obs Scanner 2: " + str(con_sc2))
            con_sc2 -= 1
            if(con_sc2 == 0):
                obstaculo_scanner2 = False
        
        #print("Con_sc1: " + str(con_sc1))
        
        if(con_desliga_agv > 0):
            con_desliga_agv -= 1
         
        #Aciona ou desliga buzina
        #if(buzzOn == True):
        #    pub_buzina.publish(True)
        #else:
        #    pub_buzina.publish(False)
            
         
        con_pose += 1
        if(con_pose > 10):
            erro_pose = True
        
        #Para sair da reducao de velocidade
        if(con_reducao > 0):
            pub_reduz.publish(True)
            con_reducao -= 1
        else:
            pub_reduz.publish(False)
        
        if(con_carregador > 0):
            con_carregador -= 1
            if (con_carregador == 0):
                modo_carregador = False
                liberado = True
                intervencao_stop = False
                parado_automatico = False
                parado_cruzamento = False
                parado_tag = False
                liga_agv = True
                con_init = 100
        
        
        pub_estado.publish(estadoAtual)           
        rate.sleep()


