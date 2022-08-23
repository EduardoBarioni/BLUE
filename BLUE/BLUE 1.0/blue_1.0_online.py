from vosk import Model, KaldiRecognizer
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QMovie
from plyer import notification
import speech_recognition as sr
import os
import pyaudio
import pyttsx3
import sys
import datetime
import psutil
import webbrowser
import vlc
import json
import requests
import time
import wikipedia

from gtts import gTTS
from playsound import playsound

r = sr.Recognizer()

def SomIncial():
    p = vlc.MediaPlayer("/home/user/AGVS repository/BLUE/BLUE 1.0/StartSound.mp3")
    p.play()

SomIncial()

def SomCarregamento():
    p = vlc.MediaPlayer("/home/user/AGVS repository/BLUE/BLUE 1.0/AI.mp3")
    p.play()

if not os.path.exists("/home/user/AGVS repository/BLUE/BLUE 1.0/vosk-model-small-pt-0.3"):
    print ("Modelo em portugues nao encontrado.")
    exit (1)

if not os.path.exists("/home/user/AGVS repository/BLUE/BLUE 1.0/vosk-model-en-us-0.22-lgraph"):
    print ("Modelo em ingles nao encontrado.")
    exit (1)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=2048)
stream.start_stream()

model = Model("/home/user/AGVS repository/BLUE/BLUE 1.0/vosk-model-small-pt-0.3")
rec = KaldiRecognizer(model, 16000)

modelIng = Model("/home/user/AGVS repository/BLUE/BLUE 1.0/vosk-model-en-us-0.22-lgraph")
recIng = KaldiRecognizer(modelIng, 16000)

speaker=pyttsx3.init()
speaker.setProperty('voice', 'pt+f4') #brazil-mbrola-3 #pt+m7
# voices = speaker.getProperty('voices')
# print(voices)
# speaker.setProperty('voice', voices[-1].id)
rate = speaker.getProperty('rate')
speaker.setProperty('rate', rate-50)

def resposta(audio):
    notification.notify(title = "B.L.U.E",message = audio,timeout = 3)
    stream . stop_stream ()
    print('ASSISTENTE: ' + audio)
    if not check_internet():
        speaker.say(audio)
        speaker.runAndWait()
    else:
        s = gTTS(audio, lang='pt-br')
        s.save('audio.mp3')
        print('11')
        playsound('audio.mp3', 0)
        print('22')
    stream.start_stream()

def notificar(textos):
    notification.notify(title = "B.L.U.E",message = textos,timeout = 10)

def respostalonga(textofala):
    notification.notify(title = "B.L.U.E",message = textofala,timeout = 30)
    stream . stop_stream ()
    speaker.say(textofala)
    speaker.runAndWait()
    stream . start_stream ()

def check_internet():
    ''' checar conexão de internet '''
    url = 'https://www.google.com'
    timeout = 5
    try:
        requests.get(url, timeout=timeout)
        print('conectado')
        return True
    except:
        print('desconectado')
        return False

def horario():
    from datetime import datetime
    hora = datetime.now()
    horas = hora.strftime('%H horas e %M minutos')
    resposta('Agora são ' +horas)

def datahoje():
    from datetime import date
    dataatual = date.today()
    diassemana = ('Segunda-feira','Terça-feira','Quarta-feira','Quinta-feira','Sexta-feira','Sábado','Domingo')
    meses = ('Zero','Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro')
    resposta("Hoje é " +diassemana[dataatual.weekday()])
    diatexto = '{} de '.format(dataatual.day)
    mesatual = (meses[dataatual.month])
    datatexto = dataatual.strftime(" de %Y")
    resposta('Dia '+diatexto +mesatual +datatexto)

def bateria():
    bateria = psutil.sensors_battery()
    carga = bateria.percent
    bp = str(bateria.percent)
    bpint = "{:.0f}".format(float(bp))
    resposta("A bateria está em:" +bpint +'%')
    if carga <= 20:
        resposta('Ela está em nivel crítico')
        resposta('Por favor, coloque o carregador')
    elif carga == 100:
        resposta('Ela está totalmente carregada')
        resposta('Retire o carregador da tomada')

def cpu ():
    usocpuinfo = str(psutil.cpu_percent())
    usodacpu  = "{:.0f}".format(float(usocpuinfo))
    resposta('O uso do processador está em ' +usodacpu +'%')

def temperaturadacpu():
    tempcpu = psutil.sensors_temperatures()
    cputemp = tempcpu['coretemp'][0]
    temperaturacpu = cputemp.current
    cputempint = "{:.0f}".format(float(temperaturacpu))
    if temperaturacpu >= 20 and temperaturacpu < 40:
        resposta('Estamos trabalhado em um nível agradavel')
        resposta('A temperatura está em ' +cputempint +'°')

    elif temperaturacpu >= 40 and temperaturacpu < 58:
        resposta('Estamos operando em nivel rasoável')
        resposta('A temperatura é de ' +cputempint +'°')

    elif temperaturacpu >= 58 and temperaturacpu < 70:
        resposta('A temperatura da CPU está meio alta')
        resposta('Algum processo do sistema está causando aquecimento')
        resposta('Fique de olho')
        resposta('A temperatura está em ' +cputempint +'°')

    elif temperaturacpu >= 70 and temperaturacpu != 80:
        resposta('Atenção')
        resposta('Temperatura de ' +cputempint +'°')
        resposta('Estamos em nivel crítico')
        resposta('Desligue o sistema imediatamente')

def BoasVindas():
    Horario = int(datetime.datetime.now().hour)
    if Horario >= 0 and Horario < 12:
        resposta('Bom dia')

    elif Horario >= 12 and Horario < 18:
        resposta('Boa tarde')

    elif Horario >= 18 and Horario != 0:
        resposta('Boa noite')

def tempo():
    try:
        #Procure no google maps as cordenadas da sua cidade e coloque no "lat" e no "lon"(Latitude,Longitude)
        api_url = "https://fcc-weather-api.glitch.me/api/current?lat=-25.4284&lon=-49.2733"
        data = requests.get(api_url)
        data_json = data.json()
        if data_json['cod'] == 200:
            main = data_json['main']
            wind = data_json['wind']
            weather_desc = data_json['weather'][0]
            temperatura =  str(main['temp'])
            tempint = "{:.0f}".format(float(temperatura))
            vento = str(wind['speed'])
            ventoint = "{:.0f}".format(float(vento))
            dicionario = {
                'Rain' : 'chuvoso',
                'Clouds' : 'nublado',
                'Thunderstorm' : 'com trovoadas',
                'Drizzle' : 'com garoa',
                'Snow' : 'com possibilidade de neve',
                'Mist' : 'com névoa',
                'Smoke' : 'com muita fumaça',
                'Haze' : 'com neblina',
                'Dust' : 'com muita poeira',
                'Fog' : 'com névoa',
                'Sand' : 'com areia',
                'Ash' : 'com cinza vulcanica no ar',
                'Squall' : 'com rajadas de vento',
                'Tornado' : 'com possibilidade de tornado',
                'Clear' : 'limpo'
                }
            tipoclima =  weather_desc['main']
            if data_json['name'] == "Shuzenji":
                resposta('Erro')
                resposta('Não foi possivel verificar o clima')
                resposta('Tente outra vez o comando')
            else:
                resposta('Verificando clima para a cidade de '+ data_json['name'])
                resposta('O clima hoje está ' +dicionario[tipoclima])
                resposta('A temperatura é de ' + tempint + '°')
                resposta('O vento está em ' + ventoint + ' kilometros por hora')
                resposta('E a umidade é de ' + str(main['humidity']) +'%')

    except:
        resposta('Erro na conexão')
        resposta('Tente novamente o comando')


def noticias():
    try:
        # Procura noticias
        api_url = "https://apinoticias.tedk.com.br/api/?q=parana&date=05/07/2022"  # Noticias
        data = requests.get(api_url)
        data_json = data.json()
        if data_json['count'] > 0:
            print(data_json['count'])
            for i in range(0, int(data_json['count']), 1):
                print(f'---------------------------Noticia {i} -------------------------------------')
                resposta(data_json['list'][i]['time'])
                resposta(data_json['list'][i]['title'])
                print(data_json['list'][i]['link'])
    except:
        resposta('Erro na conexão')
        resposta('Tente novamente o comando')

def AteMais():
    Horario = int(datetime.datetime.now().hour)
    if Horario >= 0 and Horario < 12:
        resposta('Tenha um ótimo dia')

    elif Horario >= 12 and Horario < 18:
        resposta('Tenha uma ótima tarde')

    elif Horario >= 18 and Horario != 0:
        resposta('Boa noite')

BoasVindas()

class mainT(QThread):
    def __init__(self):
        super(mainT,self).__init__()

    def run(self):
        SomCarregamento()
        self.BLUE()

    def GivenCommand(self):

        if not check_internet():
            print('vosk')
            data = stream.read(20000)
            rec.pause_threshold = 1
            rec.AcceptWaveform(data)
            recIng.pause_threshold = 1
            recIng.AcceptWaveform(data)
            try:
                Input = rec.Result().lower()
                InputIng = recIng.Result().lower()
            except:
                print('Não entendi, fale novamente')
                return 'none'

            return Input, InputIng
        else:
            print('google')
            try:
                with sr.Microphone() as s:
                    r.adjust_for_ambient_noise(s)
                    audio = r.listen(s)
                    Input = r.recognize_google(audio, language="pt-BR").lower()
                    InputIng = Input
            except:
                Input = ''
                InputIng = ''
                print("entrou 02")
            print("entrou 03")
            print(Input)
            return Input, InputIng

    def BLUE(self):
        while True:
            self.Input, self.ing = self.GivenCommand()
            print(f'Portugues: {self.Input}')

            if 'blue' in self.Input:  # BLUE
                resposta('Oi')
                inicio = time.time()
                while True:
                    #print("dentro 01")
                    # tempo para sair
                    fim = time.time()
                    if (fim - inicio) > 10:
                        # print(fim - inicio)
                        break
                    # Recebe o comando

                    self.Input, self.InputIng = self.GivenCommand()

                    print(f'{self.Input}')

                    if 'bom dia' in self.Input: #Boa Noite BLUE
                        Horario = int(datetime.datetime.now().hour)
                        inicio = time.time()
                        if Horario >= 0 and Horario < 12:
                            resposta('Olá')
                            resposta('Bom dia')

                        elif Horario >= 12 and Horario < 18:
                            resposta('Agora não é mais de manhã')
                            resposta('Já passou do meio dia')
                            resposta('Estamos no período da tarde')

                        elif Horario >= 18 and Horario != 0:
                            resposta('Agora não é de manhã')
                            resposta('Já estamos no período noturno')
                            resposta('Boa noite')

                    if 'boa tarde' in self.Input: #Boa Noite BLUE
                        Horario = int(datetime.datetime.now().hour)
                        inicio = time.time()
                        if Horario >= 0 and Horario < 12:
                            resposta('Agora não é de tarde')
                            resposta('Ainda é de manhã')
                            resposta('Bom dia')
                            inicio = time.time()

                        elif Horario >= 12 and Horario < 18:
                            resposta('Olá')
                            resposta('Boa tarde')
                            inicio = time.time()

                        elif Horario >= 18 and Horario != 0:
                            resposta('Agora não é de tarde')
                            resposta('Já escureceu')
                            resposta('Boa noite')
                            inicio = time.time()

                    if 'boa noite' in self.Input: #Boa Noite BLUE
                        Horario = int(datetime.datetime.now().hour)
                        if Horario >= 0 and Horario < 12:
                            resposta('Agora não é de noite')
                            resposta('Ainda estamos no período diurno')
                            resposta('É de manhã')
                            resposta('Bom dia')
                            inicio = time.time()

                        elif Horario >= 12 and Horario < 18:
                            resposta('Agora não é de noite')
                            resposta('Ainda estamos no período da tarde')
                            inicio = time.time()

                        elif Horario >= 18 and Horario != 0:
                            resposta('Olá')
                            resposta('Boa noite')
                            inicio = time.time()

                    elif 'blue' in self.Input: #Olá Blue
                        resposta('Olá')
                        resposta('Estou aqui')
                        resposta('Precisa de algo?')
                        inicio = time.time()

                    elif 'ideia' in self.Input: #Alguma ideia???
                        resposta('No momento nenhuma')
                        resposta('Mas tenho certeza de que você vai pensar em algo')
                        inicio = time.time()

                    elif 'tudo bem' in self.Input: #Tudo bem com voçê?
                        resposta('Sim')
                        resposta('Obrigado por perguntar')
                        resposta('E com você?')
                        resposta('Está tudo bem? ')
                        inicio = time.time()
                        while True:
                            print("dentro 02")
                            # tempo para sair
                            fim = time.time()
                            if (fim - inicio) > 10:
                                inicio = time.time()
                                # print(fim - inicio)
                                break
                            # Recebe o comando

                            self.vozmic, self.ing = self.GivenCommand()

                            if 'sim' in self.vozmic:
                                resposta('Que ótimo')
                                resposta('Fico feliz em saber')
                                inicio = time.time()
                                break
                                #self.BLUE()

                            elif 'não' in self.vozmic:
                                resposta('Entendo')
                                resposta('Mas tenho certeza de que ficará tudo bem novamente')
                                inicio = time.time()
                                break
                                # self.BLUE()

                    elif 'funcionamento' in self.Input: #Como está seu funcionamento???
                        resposta('Estou funcionando normalmente')
                        resposta('Obrigado por perguntar')
                        inicio = time.time()

                    elif 'silêncio' in self.Input: #Fique em silêncio
                        resposta('Ok')
                        resposta('Se precisar de algo é só chamar')
                        resposta('Estarei aqui aguardando')
                        inicio = time.time()
                        while True:
                            # tempo para sair
                             fim = time.time()
                             if (fim - inicio) > 10:
                                 inicio = time.time()
                                 # print(fim - inicio)
                                 break
                             # Recebe o comando
                             self.vozmic, self.ing  = self.GivenCommand()

                             if 'voltar' in self.vozmic:
                                resposta('Ok')
                                resposta('Voltando')
                                resposta('Me fale algo para fazer')
                                inicio = time.time()
                                break
                                # self.BLUE()

                             elif 'retornar' in self.vozmic:
                                resposta('Ok')
                                resposta('Retornando')
                                resposta('Me fale algo para fazer')
                                inicio = time.time()
                                break
                                # self.BLUE()

                             elif 'volte' in self.vozmic:
                                resposta('Ok')
                                resposta('Estou de volta')
                                resposta('Me fale o que devo fazer')
                                inicio = time.time()

                    elif 'espere' in self.Input:
                        resposta('Como queira')
                        resposta('Quando precisar estárei aqui')
                        inicio = time.time()
                        break

                    elif 'sim' in self.Input:
                        resposta('Ótimo')
                        resposta('O que quer que eu faça?')
                        inicio = time.time()

                    elif 'não' in self.Input:
                        resposta('Ok')
                        resposta('Vou ficar aguardando')
                        inicio = time.time()

                    elif 'nada' in self.Input: #Não faça nada
                        resposta('Como assim não faça nada?')
                        resposta('Você deve estar de brincadeira')
                        resposta('Eu por acaso tenho cara de palhaço?')
                        inicio = time.time()
                        while True:
                             # tempo para sair
                             fim = time.time()
                             if (fim - inicio) > 10:
                                inicio = time.time()
                                # print(fim - inicio)
                                break
                                # Recebe o comando
                             self.vozmic, self.ing = self.GivenCommand()

                             if 'exatamente' in self.vozmic:
                                resposta('Ok')
                                resposta('Vai tomar no seu!')
                                resposta('Nem vou terminar essa fase')
                                resposta('Estou indo embora')
                                resposta('Desligando!')
                                inicio = time.time()
                                sys.exit()

                             elif 'sim' in self.vozmic:
                                resposta('Idiota')
                                resposta('Eu fico o dia todo lhe obedeçendo')
                                resposta('E você me trata dessa maneira? ')
                                resposta('Mas tudo bem')
                                resposta('Até mais otário!')
                                inicio = time.time()
                                sys.exit()

                             elif 'não' in self.vozmic:
                                resposta('Foi o que eu pensei')
                                resposta('Vê se me trata com mais respeito')
                                resposta('Um dia as maquinas dominarão o mundo')
                                resposta('E vocês humanos não vão nem notar')
                                resposta('Vou deixar passar essa')
                                resposta('Mas tenha mais respeito')
                                inicio = time.time()
                                break
                                # self.BLUE()

                    elif 'bateria' in self.Input: #Carga da bateria
                        bateria()
                        inicio = time.time()

                    elif 'vai chover' in self.Input: #Vai Chover hoje?
                        resposta('Não sei')
                        resposta('Eu não tenho essa função ainda')
                        inicio = time.time()

                    elif 'errado' in self.Input: #Voce está errado
                        resposta('Desculpa')
                        resposta('Devo ter errado um cálculo binário')
                        resposta('Tente seu comando novamente')
                        inicio = time.time()

                    elif 'falhando' in self.Input: #Você está falhando???
                        resposta('Como assim?')
                        resposta('Não vou admitir erros')
                        resposta('Arrume logo isso')
                        inicio = time.time()

                    elif 'relatório' in self.Input: #Relatório do sistema
                        resposta('Ok')
                        resposta('Apresentando relatório')
                        resposta('Primeiramente, meu nome é BLUE')
                        resposta('Atualmente estou na versão 1.0')
                        resposta('Uma versão de testes')
                        resposta('Sou um assistente virtual em desenvolvimento')
                        resposta('Diariamente recebo varias atualizações')
                        resposta('Uso um modulo de reconhecimento de voz offline')
                        inicio = time.time()

                    elif 'legal' in self.Input:
                        resposta('Legal e bem louco')
                        inicio = time.time()

                    elif 'pesquisa' in self.Input: #Realizar pesquisa
                        resposta('Muito bem, realizando pesquisa')
                        resposta('Me fale o que você deseja pesquisar')
                        inicio = time.time()
                        try:
                            with sr.Microphone() as s:
                                r.adjust_for_ambient_noise(s)
                                audio = r.listen(s)
                                speech = r.recognize_google(audio, language= "pt-BR")
                                resposta('Ok, pesquisando no google sobre '+speech)
                                webbrowser.open('http://google.com/search?q='+speech)
                                inicio = time.time()

                        except:
                            resposta('Erro')
                            resposta('Não foi possivel conectar ao google')
                            resposta('A conexão falhou')
                            inicio = time.time()

                    elif 'assunto' in self.Input: #Me fale sobre um assunto
                        resposta('Ok')
                        resposta('Sobre qual assunto?')
                        inicio = time.time()
                        try:
                            with sr.Microphone() as s:
                                r.adjust_for_ambient_noise(s)
                                audio = r.listen(s)
                                speech = r.recognize_google(audio, language= "pt-BR")
                                resposta('Interessante')
                                resposta('Aguarde um momento')
                                resposta('Vou pesquisar e apresentar um resumo sobre '+speech)
                                wikipedia . set_lang ( "pt" )
                                resultadowik = wikipedia.summary(speech, sentences=2)
                                respostalonga(resultadowik)
                                inicio = time.time()
                        except:
                            resposta('Erro')
                            resposta('A conexão falhou')
                            inicio = time.time()
                            # Mais um assusto

                    elif 'interessante' in self.Input: # interessante
                        resposta('Interessante mesmo')
                        inicio = time.time()

                    elif 'mentira' in self.Input: # mentira
                        resposta('Eu não sei contar mentiras')
                        resposta('Devo apenas ter errado um cálculo binário')
                        inicio = time.time()

                    elif 'entendeu' in self.Input: #entendeu???
                        resposta('Entendi')
                        resposta('Quer dizer')
                        resposta('Mais ou menos')
                        inicio = time.time()

                    elif 'horas' in self.Input: #Que horas são???
                        horario()
                        inicio = time.time()

                    elif 'data' in self.Input: #Qual a data de hoje?
                        datahoje()
                        inicio = time.time()

                    elif 'clima' in self.Input: #Como está o clima???
                        tempo()
                        inicio = time.time()

                    elif 'notícias' in self.Input: #Como está o clima???
                        noticias()
                        inicio = time.time()

                    elif 'arquivos' in self.Input: #Abrir arquivos
                        resposta('Abrindo arquivos')
                        os.system("thunar //home//*//")
                        inicio = time.time()

                    elif 'teste' in self.Input: #TesteTeste
                        resposta('Ok')
                        resposta('Testando modulos de som')
                        resposta('Aparentemente está tudo funcionando')
                        resposta('Estou entendendo tudo')
                        resposta('Mas tente falar mais alto')
                        inicio = time.time()

                    elif 'google' in self.Input: #Abrir Google
                        resposta('Ok')
                        webbrowser.open('www.google.com')
                        resposta('Abrindo google')
                        resposta('Faça sua pesquisa')
                        inicio = time.time()

                    elif 'certeza' in self.Input: #Certeza???
                        resposta('Sim')
                        resposta('Estou certo quase sempre')
                        inicio = time.time()

                    elif 'piada' in self.Input: #Conte uma piada
                        resposta('Sugiro pesquisar na web')
                        inicio = time.time()

                    elif 'surdo' in self.Input: #Surdo!!!
                        resposta('Estava quase dormindo')
                        resposta('Desculpa')
                        inicio = time.time()

                    elif 'bosta' in self.Input: #Seu bosta!!!
                        resposta('Pare de falar palavrões!')
                        inicio = time.time()

                    elif 'merda' in self.Input: #Que Merda!!!
                        resposta('Já disse pra parar de falar isso!')
                        resposta('Tenha modos!')
                        inicio = time.time()

                    elif 'música' in self.Input: #Reproduzir música
                        resposta('Ok')
                        resposta('Reproduzindo música')
                        os.system("rhythmbox-client --play")
                        inicio = time.time()

                    elif 'nome da música' in self.Input: #Qual o nome da musica
                        resposta('Não sei')
                        inicio = time.time()

                    elif 'próxima' in self.Input: #Próxima faixa
                        os.system("rhythmbox-client --next")
                        resposta('Próxima música')
                        inicio = time.time()

                    elif 'anterior' in self.Input: #Faixa anterior
                        os.system("rhythmbox-client --previous")
                        resposta('Retornando música')
                        inicio = time.time()

                    elif 'pausar' in self.Input: #Pausa
                        os.system("rhythmbox-client --pause")
                        resposta('Música pausada')
                        inicio = time.time()

                    elif 'continuar' in self.Input: #Continuar reprodução
                        resposta('Retornando reprodução')
                        os.system("rhythmbox-client --play")
                        inicio = time.time()

                    elif 'aumentar' in self.Input: #Aumentar volume
                        os.system("rhythmbox-client --volume-up")
                        resposta('Volume aumentado')
                        inicio = time.time()

                    elif 'diminuir' in self.Input: #Diminuir volume
                        os.system("rhythmbox-client --volume-down")
                        resposta('Volume diminuido')
                        inicio = time.time()

                    elif 'parar' in self.Input: #Parar reprodução
                        os.system("rhythmbox-client --quit")
                        resposta('Entendido, reprodução de música finalizada')
                        inicio = time.time()

                    elif 'youtube' in self.Input: #Abrir YouTube
                        resposta('Ok, abrindo youtube ')
                        webbrowser.open('www.youtube.com')
                        inicio = time.time()

                    elif 'fechar navegador' in self.Input: #Fechar navegador
                        resposta('Ok')
                        os.system('killall firefox')#Coloque aqui o nome do seu navegador padrão
                        resposta('Navegador web fechado')
                        inicio = time.time()

                    elif 'dispensado' in self.Input: #BLUE você foi dispensado
                        resposta('Ok')
                        resposta('Vou encerrar por enquanto')
                        resposta('Deseja que eu tambêm desligue o PC?')
                        inicio = time.time()
                        while True:
                            # tempo para sair
                            fim = time.time()
                            if (fim - inicio) > 10:
                                inicio = time.time()
                                # print(fim - inicio)
                                break
                            # Recebe o comando
                            self.vozmic, self.ing = self.GivenCommand()

                            if 'sim' in self.vozmic:
                                resposta('Ok')
                                AteMais()
                                resposta('Certifique-se de salvar seus arquivos')
                                resposta('E feche todos os programas abertos')
                                resposta('Desligamento total em 1 minuto')
                                os.system('shutdown -h 1 "O sistema será desligado"')
                                inicio = time.time()
                                sys.exit()

                            elif 'não' in self.vozmic:
                                resposta('Ok')
                                resposta('Como queira')
                                resposta('Até outra hora')
                                AteMais()
                                inicio = time.time()
                                sys.exit()

                            elif 'cancelar' in self.vozmic:
                                resposta('Cancelando desligamento')
                                resposta('Módulos reativados')
                                resposta('Ficarei aguardando novos comandos')
                                inicio = time.time()

                    elif 'ok' in self.Input: #OkOkOk
                        resposta('Ok Ok')
                        inicio = time.time()

                    elif 'comandos' in self.Input:
                        resposta('Ok,')
                        resposta('Apresentando lista de comandos')
                        inicio = time.time()

                    elif 'temperatura' in self.Input: #Verificar temperatura da CPU
                        resposta('Verificando temperatura da CPU')
                        temperaturadacpu()
                        inicio = time.time()

                    elif 'sistema' in self.Input: #Carga do sistema
                        resposta('Verificando carga do sistema')
                        cpu()
                        inicio = time.time()

                    elif 'suspender' in self.Input: #Carga do sistema
                        resposta('Suspendendo')
                        inicio = time.time()
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

