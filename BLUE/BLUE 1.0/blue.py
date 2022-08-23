from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QMovie
import os

import sys
import datetime
import psutil
import webbrowser

import json
import requests
import time
import wikipedia
import pandas as pd
from pandas import json_normalize

#import pywhatkit

import util
import escuta
import fala
import sons
timeOut = 10

sons.SomIncial()
util.BoasVindas()
fala.resposta('Tudo bem Duda')
fala.resposta('Você quer brincar?')

class mainT(QThread):
    def __init__(self):
        super(mainT,self).__init__()

    def run(self):
        sons.SomCarregamento()
        self.BLUE()

    def BLUE(self):
        while True:
            self.Input, self.InputIng = escuta.GivenCommand()
            #print("fora")
            print(f'Portugues: {self.Input}')
            print(f'Ingles: {self.InputIng}')

            if 'blue' in self.InputIng:  # BLUE
                sons.SomCarregamento()
                inicio = time.time()
                while True:
                    print("dentro 01")
                    # tempo para sair
                    fim = time.time()
                    if (fim - inicio) > timeOut:
                        # print(fim - inicio)
                        sons.SomRetorno()
                        break
                    # Recebe o comando

                    self.Input, self.InputIng = escuta.GivenCommand()

                    print(f'{self.Input}')

                    if 'bom dia' in self.Input: #Boa Noite BLUE
                        Horario = int(datetime.datetime.now().hour)
                        inicio = time.time()
                        if Horario >= 0 and Horario < 12:
                            fala.resposta('Olá')
                            fala.resposta('Bom dia')

                        elif Horario >= 12 and Horario < 18:
                            fala.resposta('Agora não é mais de manhã')
                            fala.resposta('Já passou do meio dia')
                            fala.resposta('Estamos no período da tarde')

                        elif Horario >= 18 and Horario != 0:
                            fala.resposta('Agora não é de manhã')
                            fala.resposta('Já estamos no período noturno')
                            fala.resposta('Boa noite')

                    if 'boa tarde' in self.Input: #Boa Noite BLUE
                        Horario = int(datetime.datetime.now().hour)
                        inicio = time.time()
                        if Horario >= 0 and Horario < 12:
                            fala.resposta('Agora não é de tarde')
                            fala.resposta('Ainda é de manhã')
                            fala.resposta('Bom dia')
                            inicio = time.time()

                        elif Horario >= 12 and Horario < 18:
                            fala.resposta('Olá')
                            fala.resposta('Boa tarde')
                            inicio = time.time()

                        elif Horario >= 18 and Horario != 0:
                            fala.resposta('Agora não é de tarde')
                            fala.resposta('Já escureceu')
                            fala.resposta('Boa noite')
                            inicio = time.time()

                    if 'boa noite' in self.Input: #Boa Noite BLUE
                        Horario = int(datetime.datetime.now().hour)
                        if Horario >= 0 and Horario < 12:
                            fala.resposta('Agora não é de noite')
                            fala.resposta('Ainda estamos no período diurno')
                            fala.resposta('É de manhã')
                            fala.resposta('Bom dia')
                            inicio = time.time()

                        elif Horario >= 12 and Horario < 18:
                            fala.resposta('Agora não é de noite')
                            fala.resposta('Ainda estamos no período da tarde')
                            inicio = time.time()

                        elif Horario >= 18 and Horario != 0:
                            fala.resposta('Olá')
                            fala.resposta('Boa noite')
                            inicio = time.time()

                    elif 'blue' in self.InputIng: #Olá Blue
                        fala.resposta('Olá')
                        fala.resposta('Estou aqui')
                        fala.resposta('Precisa de algo?')
                        inicio = time.time()

                    elif 'projeto' in self.Input: #criar projeto
                        util.projeto()
                        inicio = time.time()
                        break

                    elif 'tudo bem' in self.Input: #Tudo bem com voçê?
                        fala.resposta('Sim')
                        fala.resposta('Obrigado por perguntar')
                        fala.resposta('E com você?')
                        fala.resposta('Está tudo bem? ')
                        inicio = time.time()
                        while True:
                            print("dentro 02")
                            # tempo para sair
                            fim = time.time()
                            if (fim - inicio) > timeOut:
                                inicio = time.time()
                                sons.SomRetorno()
                                # print(fim - inicio)
                                break
                            # Recebe o comando

                            self.vozmic, self.vozmicIng  = escuta.GivenCommand()

                            if 'sim' in self.vozmic:
                                fala.resposta('Que ótimo')
                                fala.resposta('Fico feliz em saber')
                                inicio = time.time()
                                break
                                #self.BLUE()

                            elif 'não' in self.vozmic:
                                fala.resposta('Entendo')
                                fala.resposta('Mas tenho certeza de que ficará tudo bem novamente')
                                inicio = time.time()
                                break
                                # self.BLUE()

                    elif 'funcionamento' in self.Input: #Como está seu funcionamento???
                        fala.resposta('Estou funcionando normalmente')
                        fala.resposta('Obrigado por perguntar')
                        inicio = time.time()

                    elif 'silêncio' in self.Input: #Fique em silêncio
                        fala.resposta('Ok')
                        fala.resposta('Se precisar de algo é só chamar')
                        fala.resposta('Estarei aqui aguardando')
                        inicio = time.time()
                        while True:
                            # tempo para sair
                             fim = time.time()
                             if (fim - inicio) > timeOut:
                                 inicio = time.time()
                                 sons.SomRetorno()
                                 # print(fim - inicio)
                                 break
                             # Recebe o comando
                             self.vozmic, self.vozmicIng  = escuta.GivenCommand()

                             if 'voltar' in self.vozmic:
                                fala.resposta('Ok')
                                fala.resposta('Voltando')
                                fala.resposta('Me fale algo para fazer')
                                inicio = time.time()
                                break
                                # self.BLUE()

                             elif 'retornar' in self.vozmic:
                                fala.resposta('Ok')
                                fala.resposta('Retornando')
                                fala.resposta('Me fale algo para fazer')
                                inicio = time.time()
                                break
                                # self.BLUE()

                             elif 'volte' in self.vozmic:
                                fala.resposta('Ok')
                                fala.resposta('Estou de volta')
                                fala.resposta('Me fale o que devo fazer')
                                inicio = time.time()

                    elif 'espere' in self.Input:
                        fala.resposta('Como queira')
                        fala.resposta('Quando precisar estárei aqui')
                        inicio = time.time()
                        break

                    elif 'sim' in self.Input:
                        fala.resposta('Ótimo')
                        fala.resposta('O que quer que eu faça?')
                        inicio = time.time()

                    elif 'não' in self.Input:
                        fala.resposta('Ok')
                        fala.resposta('Vou ficar aguardando')
                        inicio = time.time()

                    elif 'nada' in self.Input: #Não faça nada
                        fala.resposta('Como assim não faça nada?')
                        fala.resposta('Você deve estar de brincadeira')
                        fala.resposta('Eu por acaso tenho cara de palhaço?')
                        inicio = time.time()
                        while True:
                             # tempo para sair
                             fim = time.time()
                             if (fim - inicio) > timeOut:
                                inicio = time.time()
                                sons.SomRetorno()
                                # print(fim - inicio)
                                break
                                # Recebe o comando
                             self.vozmic, self.vozmicIng  = escuta.GivenCommand()

                             if 'exatamente' in self.vozmic:
                                fala.resposta('Ok')
                                fala.resposta('Vai tomar no seu!')
                                fala.resposta('Nem vou terminar essa fase')
                                fala.resposta('Estou indo embora')
                                fala.resposta('Desligando!')
                                inicio = time.time()
                                sys.exit()

                             elif 'sim' in self.vozmic:
                                fala.resposta('Idiota')
                                fala.resposta('Eu fico o dia todo lhe obedeçendo')
                                fala.resposta('E você me trata dessa maneira? ')
                                fala.resposta('Mas tudo bem')
                                fala.resposta('Até mais otário!')
                                inicio = time.time()
                                sys.exit()

                             elif 'não' in self.vozmic:
                                fala.resposta('Foi o que eu pensei')
                                fala.resposta('Vê se me trata com mais respeito')
                                fala.resposta('Um dia as maquinas dominarão o mundo')
                                fala.resposta('E vocês humanos não vão nem notar')
                                fala.resposta('Vou deixar passar essa')
                                fala.resposta('Mas tenha mais respeito')
                                inicio = time.time()
                                break
                                # self.BLUE()

                    elif 'bateria' in self.Input: #Carga da bateria
                        util.bateria()
                        inicio = time.time()

                    elif 'vai chover' in self.Input: #Vai Chover hoje?
                        fala.resposta('Não sei')
                        fala.resposta('Eu não tenho essa função ainda')
                        inicio = time.time()

                    elif 'errado' in self.Input: #Voce está errado
                        fala.resposta('Desculpa')
                        fala.resposta('Devo ter errado um cálculo binário')
                        fala.resposta('Tente seu comando novamente')
                        inicio = time.time()

                    elif 'falhando' in self.Input: #Você está falhando???
                        fala.resposta('Como assim?')
                        fala.resposta('Não vou admitir erros')
                        fala.resposta('Arrume logo isso')
                        inicio = time.time()

                    elif 'relatório' in self.Input: #Relatório do sistema
                        util.bateria()
                        util.temperaturadacpu()
                        util.cpu()
                        inicio = time.time()
                        sons.SomRetorno()

                    elif 'pesquisa' in self.Input: #Realizar pesquisa
                        fala.resposta('Muito bem, realizando pesquisa')
                        fala.resposta('Me fale o que você deseja pesquisar')
                        inicio = time.time()
                        try:
                            self.vozmic, self.vozmicIng = escuta.GivenCommand()
                            fala.resposta('Ok, pesquisando no google sobre '+ self.vozmic)
                            #webbrowser.open('http://google.com/search?q='+speech)
                            try:
                                #pywhatkit.search(self.vozmic)
                                print("Searching...")
                            except:
                                print("An unknown error occured")
                            inicio = time.time()

                        except:
                            fala.resposta('Erro')
                            fala.resposta('Não foi possivel conectar ao google')
                            fala.resposta('A conexão falhou')
                            inicio = time.time()

                    elif 'assunto' in self.Input: #Me fale sobre um assunto
                        fala.resposta('Ok')
                        fala.resposta('Sobre qual assunto?')
                        inicio = time.time()
                        try:
                            self.vozmic, self.vozmicIng = escuta.GivenCommand()
                            fala.resposta('Ok, pesquisando no google sobre ' + self.vozmic)
                            fala.resposta('Interessante')
                            fala.resposta('Aguarde um momento')
                            fala.resposta('Vou pesquisar e apresentar um resumo sobre '+self.vozmic)
                            try:
                                #fala.respostalonga(pywhatkit.info(self.vozmic, lines=4))
                                print("\nSuccessfully Searched")
                            except:
                                print("An Unknown Error Occured")

                            #wikipedia.set_lang ("pt")
                            #resultadowik = wikipedia.summary(speech, sentences=2)
                            #respostalonga(resultadowik)
                            inicio = time.time()
                        except:
                            fala.resposta('Erro')
                            fala.resposta('A conexão falhou')
                            inicio = time.time()
                            # Mais um assusto

                    elif 'horas' in self.Input: #Que horas são???
                        util.horario()
                        inicio = time.time()

                    elif 'horário' in self.Input: #Que horas são???
                        util.horario()
                        inicio = time.time()

                    elif 'data' in self.Input: #Qual a data de hoje?
                        util.datahoje()
                        inicio = time.time()

                    elif 'clima' in self.Input: #Como está o clima???
                        util.tempo()
                        inicio = time.time()

                    elif 'tempo' in self.Input: #Como está o clima???
                        util.tempo()
                        inicio = time.time()

                    elif 'notícias' in self.Input: #Como está o clima???
                        util.noticias()
                        inicio = time.time()

                    elif 'notícia' in self.Input: #Como está o clima???
                        util.noticias()
                        inicio = time.time()

                    elif 'arquivos' in self.Input: #Abrir arquivos
                        fala.resposta('Abrindo arquivos')
                        os.system("thunar //home//*//")
                        inicio = time.time()

                    elif 'teste' in self.Input: #TesteTeste
                        fala.resposta('Ok')
                        fala.resposta('Testando modulos de som')
                        fala.resposta('Aparentemente está tudo funcionando')
                        inicio = time.time()

                    elif 'google' in self.Input: #Abrir Google
                        fala.resposta('Ok')
                        webbrowser.open('www.google.com')
                        fala.resposta('Abrindo google')
                        fala.resposta('Faça sua pesquisa')
                        inicio = time.time()

                    elif 'piada' in self.Input: #Conte uma piada
                        util.piada()
                        inicio = time.time()

                    elif 'conselho' in self.Input: #Conte uma piada
                        util.conselho()
                        inicio = time.time()

                    elif 'surdo' in self.Input: #Surdo!!!
                        fala.resposta('Estava quase dormindo')
                        fala.resposta('Desculpa')
                        inicio = time.time()

                    elif 'bosta' in self.Input: #Seu bosta!!!
                        fala.resposta('Pare de falar palavrões!')
                        inicio = time.time()

                    elif 'merda' in self.Input: #Que Merda!!!
                        fala.resposta('Já disse pra parar de falar isso!')
                        fala.resposta('Tenha modos!')
                        inicio = time.time()

                    elif 'música' in self.Input: #Reproduzir música
                        fala.resposta('Ok')
                        fala.resposta('Reproduzindo música')
                        os.system("rhythmbox-client --play")
                        inicio = time.time()

                    elif 'nome da música' in self.Input: #Qual o nome da musica
                        fala.resposta('Não sei')
                        inicio = time.time()

                    elif 'próxima' in self.Input: #Próxima faixa
                        os.system("rhythmbox-client --next")
                        fala.resposta('Próxima música')
                        inicio = time.time()

                    elif 'anterior' in self.Input: #Faixa anterior
                        os.system("rhythmbox-client --previous")
                        fala.resposta('Retornando música')
                        inicio = time.time()

                    elif 'pausar' in self.Input: #Pausa
                        os.system("rhythmbox-client --pause")
                        fala.resposta('Música pausada')
                        inicio = time.time()

                    elif 'continuar' in self.Input: #Continuar reprodução
                        fala.resposta('Retornando reprodução')
                        os.system("rhythmbox-client --play")
                        inicio = time.time()

                    elif 'aumentar' in self.Input: #Aumentar volume
                        os.system("rhythmbox-client --volume-up")
                        fala.resposta('Volume aumentado')
                        inicio = time.time()

                    elif 'diminuir' in self.Input: #Diminuir volume
                        os.system("rhythmbox-client --volume-down")
                        fala.resposta('Volume diminuido')
                        inicio = time.time()

                    elif 'parar' in self.Input: #Parar reprodução
                        os.system("rhythmbox-client --quit")
                        fala.resposta('Entendido, reprodução de música finalizada')
                        inicio = time.time()

                    elif 'youtube' in self.Input: #Abrir YouTube
                        fala.resposta('Ok, abrindo youtube ')
                        webbrowser.open('www.youtube.com')
                        inicio = time.time()

                    elif 'fechar navegador' in self.Input: #Fechar navegador
                        fala.resposta('Ok')
                        os.system('killall firefox')#Coloque aqui o nome do seu navegador padrão
                        fala.resposta('Navegador web fechado')
                        inicio = time.time()

                    elif 'dispensado' in self.Input: #BLUE você foi dispensado
                        fala.resposta('Ok')
                        fala.resposta('Vou encerrar por enquanto')
                        fala.resposta('Deseja que eu tambêm desligue o PC?')
                        inicio = time.time()
                        while True:
                            # tempo para sair
                            fim = time.time()
                            if (fim - inicio) > timeOut:
                                inicio = time.time()
                                # print(fim - inicio)
                                break
                            # Recebe o comando
                            self.vozmic = escuta.GivenCommand()

                            if 'sim' in self.vozmic:
                                fala.resposta('Ok')
                                util.AteMais()
                                fala.resposta('Certifique-se de salvar seus arquivos')
                                fala.resposta('E feche todos os programas abertos')
                                fala.resposta('Desligamento total em 1 minuto')
                                os.system('shutdown -h 1 "O sistema será desligado"')
                                inicio = time.time()
                                sys.exit()

                            elif 'não' in self.vozmic:
                                fala.resposta('Ok')
                                fala.resposta('Como queira')
                                fala.resposta('Até outra hora')
                                util.AteMais()
                                inicio = time.time()
                                sys.exit()

                            elif 'cancelar' in self.vozmic:
                                fala.resposta('Cancelando desligamento')
                                fala.resposta('Módulos reativados')
                                fala.resposta('Ficarei aguardando novos comandos')
                                inicio = time.time()

                    elif 'comandos' in self.Input:
                        fala.resposta('Ok,')
                        fala.resposta('Apresentando lista de comandos')
                        inicio = time.time()
                        sons.SomRetorno()

                    elif 'temperatura' in self.Input: #Verificar temperatura da CPU
                        fala.resposta('Verificando temperatura da CPU')
                        util.temperaturadacpu()
                        inicio = time.time()
                        sons.omRetorno()

                    elif 'sistema' in self.Input: #Carga do sistema
                        fala.resposta('Verificando carga do sistema')
                        util.cpu()
                        inicio = time.time()
                        sons.SomRetorno()

                    elif 'suspender' in self.Input: #Carga do sistema
                        fala.resposta('Suspendendo')
                        inicio = time.time()
                        sons.SomRetorno()
                        break

class Janela (QMainWindow):
    def __init__(self):
        super().__init__()
        
        Dspeak = mainT()
        Dspeak.start()
        
        self.label_gif = QLabel(self)
        self.label_gif.setAlignment(QtCore.Qt.AlignCenter)
        self.label_gif.move(0,0)
        self.label_gif.resize(400,300)
        self.movie = QMovie("AnimatedBackGround.gif")
        self.label_gif.setMovie(self.movie)
        self.movie.start()
        
        self.label_blue = QLabel(self)
        self.label_blue.setText("B.L.U.E")
        self.label_blue.setAlignment(QtCore.Qt.AlignCenter)
        self.label_blue.move(0,0)
        self.label_blue.setStyleSheet('QLabel {font:bold;font-size:50px;color:#2F00FF}')
        self.label_blue.resize(400,300)
        
        self.label_cpu = QLabel(self)
        self.label_cpu.setText("Uso da CPU: 32%")
        self.label_cpu.move(8,250)
        self.label_cpu.setStyleSheet('QLabel {font-size:14px;color:#000079}')
        self.label_cpu.resize(131,20)
        cpu = QTimer(self)
        cpu.timeout.connect(self.MostrarCPU)
        cpu.start(1000)
        
        self.label_cputemp = QLabel(self)
        self.label_cputemp.setText("Temperatura: 32°")
        self.label_cputemp.move(8,270)
        self.label_cputemp.setStyleSheet('QLabel {font-size:14px;color:#000079}')
        self.label_cputemp.resize(131,20)
        tempc = QTimer(self)
        tempc.timeout.connect(self.MostrarTMP)
        tempc.start(1000)
        
        self.label_assv = QLabel(self)
        self.label_assv.setText("Assistente Virtual")
        self.label_assv.move(5,5)
        self.label_assv.setStyleSheet('QLabel {font:bold;font-size:14px;color:#000079}')
        self.label_assv.resize(200,20)

        self.label_version = QLabel(self)
        self.label_version.setText("Versão Alpha 1.0")
        self.label_version.setAlignment(QtCore.Qt.AlignCenter)
        self.label_version.move(265,270)
        self.label_version.setStyleSheet('QLabel {font-size:14px;color:#000079}')
        self.label_version.resize(131,20)
        
        self.label_JG = QLabel(self)
        self.label_JG.setText("by JGcode")
        self.label_JG.setAlignment(QtCore.Qt.AlignRight)
        self.label_JG.move(300,250)
        self.label_JG.setStyleSheet('QLabel {font-size:14px;color:#000079}')
        self.label_JG.resize(80,20)
        
        data =  QDate.currentDate()
        datahoje = data.toString('dd/MM/yyyy')
        self.label_data = QLabel(self)
        self.label_data.setText(datahoje)
        self.label_data.setAlignment(QtCore.Qt.AlignCenter)
        self.label_data.move(5,25)
        self.label_data.setStyleSheet('QLabel {font-size:14px;color:#000079}')
        self.label_data.resize(80,20)
          
        self.label_horas = QLabel(self)
        self.label_horas.setText("22:36:09")
        self.label_horas.setAlignment(QtCore.Qt.AlignCenter)
        self.label_horas.move(0,45)
        self.label_horas.setStyleSheet('QLabel {font-size:14px;color:#000079}')
        self.label_horas.resize(71,20)
        horas = QTimer(self)
        horas.timeout.connect(self.MostrarHorras)
        horas.start(1000)

        botao_fechar = QPushButton("",self)
        botao_fechar.move(370,5)
        botao_fechar.resize(20,20)
        botao_fechar.setStyleSheet("background-image : url(Fechar.png);border-radius: 15px;") 
        botao_fechar.clicked.connect(self.fechartudo)
        
        self.CarregarJanela()
    	
    def CarregarJanela(self):
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setGeometry(50,50,400,300)
        self.setMinimumSize(400, 300)
        self.setMaximumSize(400, 300)
        self.setWindowOpacity(0.95) 
        #self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        #self.setStyleSheet("background-color: black")
        self.setWindowIcon(QtGui.QIcon('Icone.png'))
        self.setWindowTitle("Assistente Virtual")
        self.show()

    def fechartudo(self):
        print('botao fechar presionado')
        sys.exit()

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.dragPos = event.globalPos()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

    def MostrarHorras(self):
        hora_atual = QTime.currentTime()
        label_time = hora_atual.toString('hh:mm:ss')
        self.label_horas.setText(label_time)

    def MostrarTMP(self):
        tempcpu = psutil.sensors_temperatures()
        cputemp = tempcpu['coretemp'][0]
        temperaturacpu = cputemp.current
        cputempint = "{:.0f}".format(float(temperaturacpu))
        self.label_cputemp.setText("Temperatura: " +cputempint +"°")
        
    def MostrarCPU(self):
        usocpu =  str(psutil.cpu_percent())
        self.label_cpu.setText("Uso da CPU: " +usocpu +"%")
		
aplicacao = QApplication(sys.argv)
j = Janela()
sys.exit(aplicacao.exec_())

