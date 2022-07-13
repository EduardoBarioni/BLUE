from vosk import Model, KaldiRecognizer
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
import pandas as pd
from pandas import json_normalize
import fala
import escuta
import sons

timeOut = 10

def check_internet():
    ''' checar conexão de internet '''
    url = 'https://www.google.com'
    timeout = 5
    try:
        requests.get(url, timeout=timeout)
        return True
    except:
        return False

def horario():
    from datetime import datetime
    hora = datetime.now()
    horas = hora.strftime('%H horas e %M minutos')
    fala.resposta('Agora são ' +horas)


def datahoje():
    from datetime import date
    dataatual = date.today()
    diassemana = ('Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo')
    meses = (
    'Zero', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro',
    'Novembro', 'Dezembro')
    fala.resposta("Hoje é " + diassemana[dataatual.weekday()])
    diatexto = '{} de '.format(dataatual.day)
    mesatual = (meses[dataatual.month])
    datatexto = dataatual.strftime(" de %Y")
    fala.resposta('Dia ' + diatexto + mesatual + datatexto)


def bateria():
    bateria = psutil.sensors_battery()
    carga = bateria.percent
    bp = str(bateria.percent)
    bpint = "{:.0f}".format(float(bp))
    fala.resposta("A bateria está em:" + bpint + '%')
    if carga <= 20:
        fala.resposta('Ela está em nivel crítico')
        fala.resposta('Por favor, coloque o carregador')
    elif carga == 100:
        fala.resposta('Ela está totalmente carregada')
        fala.resposta('Retire o carregador da tomada')


def cpu():
    usocpuinfo = str(psutil.cpu_percent())
    usodacpu = "{:.0f}".format(float(usocpuinfo))
    fala.resposta('O uso do processador está em ' + usodacpu + '%')


def temperaturadacpu():
    tempcpu = psutil.sensors_temperatures()
    cputemp = tempcpu['coretemp'][0]
    temperaturacpu = cputemp.current
    cputempint = "{:.0f}".format(float(temperaturacpu))
    if temperaturacpu >= 20 and temperaturacpu < 40:
        fala.resposta('Estamos trabalhado em um nível agradavel')
        fala.resposta('A temperatura está em ' + cputempint + '°')

    elif temperaturacpu >= 40 and temperaturacpu < 58:
        fala.resposta('Estamos operando em nivel rasoável')
        fala.resposta('A temperatura é de ' + cputempint + '°')

    elif temperaturacpu >= 58 and temperaturacpu < 70:
        fala.resposta('A temperatura da CPU está meio alta')
        fala.resposta('Algum processo do sistema está causando aquecimento')
        fala.resposta('Fique de olho')
        fala.resposta('A temperatura está em ' + cputempint + '°')

    elif temperaturacpu >= 70 and temperaturacpu != 80:
        fala.resposta('Atenção')
        fala.resposta('Temperatura de ' + cputempint + '°')
        fala.resposta('Estamos em nivel crítico')
        fala.resposta('Desligue o sistema imediatamente')


def BoasVindas():
    Horario = int(datetime.datetime.now().hour)
    if Horario >= 0 and Horario < 12:
        fala.resposta('Bom dia')

    elif Horario >= 12 and Horario < 18:
        fala.resposta('Boa tarde')

    elif Horario >= 18 and Horario != 0:
        fala.resposta('Boa noite')


def tempo():
    try:
        # Procure no google maps as cordenadas da sua cidade e coloque no "lat" e no "lon"(Latitude,Longitude)
        api_url = "https://fcc-weather-api.glitch.me/api/current?lat=-25.4284&lon=-49.2733"
        data = requests.get(api_url)
        data_json = data.json()
        if data_json['cod'] == 200:
            main = data_json['main']
            wind = data_json['wind']
            weather_desc = data_json['weather'][0]
            temperatura = str(main['temp'])
            tempint = "{:.0f}".format(float(temperatura))
            vento = str(wind['speed'])
            ventoint = "{:.0f}".format(float(vento))
            dicionario = {
                'Rain': 'chuvoso',
                'Clouds': 'nublado',
                'Thunderstorm': 'com trovoadas',
                'Drizzle': 'com garoa',
                'Snow': 'com possibilidade de neve',
                'Mist': 'com névoa',
                'Smoke': 'com muita fumaça',
                'Haze': 'com neblina',
                'Dust': 'com muita poeira',
                'Fog': 'com névoa',
                'Sand': 'com areia',
                'Ash': 'com cinza vulcanica no ar',
                'Squall': 'com rajadas de vento',
                'Tornado': 'com possibilidade de tornado',
                'Clear': 'limpo'
            }
            tipoclima = weather_desc['main']
            if data_json['name'] == "Shuzenji":
                fala.resposta('Erro')
                fala.resposta('Não foi possivel verificar o clima')
                fala.resposta('Tente outra vez o comando')
            else:
                fala.resposta('Verificando clima para a cidade de ' + data_json['name'])
                fala.resposta('O clima hoje está ' + dicionario[tipoclima])
                fala.resposta('A temperatura é de ' + tempint + '°')
                fala.resposta('O vento está em ' + ventoint + ' kilometros por hora')
                fala.resposta('E a umidade é de ' + str(main['humidity']) + '%')

    except:
        fala.resposta('Erro na conexão')
        fala.resposta('Tente novamente o comando')


def noticias():
    try:
        # Procura noticias
        api_url = "https://apinoticias.tedk.com.br/api/?q=parana&date=05/07/2022"  # Noticias
        data = requests.get(api_url)
        data_json = data.json()
        df = json_normalize(data_json['list'])
        df_noticias = df.sort_values(by=['time'], ascending=False, na_position='last').reset_index()
        if data_json['count'] > 0:
            print(data_json['count'])
            fala.resposta(f"serão {data_json['count']} notícias. Deseja escutar todas?")
            inicio = time.time()
            while True:
                # tempo para sair
                fim = time.time()
                if (fim - inicio) > 10:
                    # print(fim - inicio)
                    sons.SomCarregamento()
                    break
                # Recebe o comando
                Input, InputIng = escuta.GivenCommand()
                if 'sim' in Input:
                    i = 0
                    while i < int(data_json['count']):
                        Input, InputIng = escuta.GivenCommand()
                        if 'cancelar' in Input:
                            break
                        elif 'parar' in Input:
                            break
                        elif 'repetir' in Input:
                            i = i - 1
                        print(f'---------------------------Noticia {i} -------------------------------------')
                        print(df.columns.tolist())
                        fala.resposta(df_noticias['time'][i])
                        fala.resposta(df_noticias['title'][i])
                        # print(df_noticias['description'][i])
                        print(df_noticias['link'][i])
                        i = i + 1

                    sons.SomCarregamento()
                    break
                if 'não' in Input:
                    sons.SomCarregamento()
                    break
    except:
        fala.resposta('Erro na conexão')
        fala.resposta('Tente novamente o comando')
    i = 0


def piada():
    api_url = "https://api.chucknorris.io/jokes/random"  # Chuck Norris
    data = requests.get(api_url)
    data_json = data.json()
    # print(data_json)
    df = json_normalize(data_json)
    # df = df.sort_values(by=['value'], ascending=False, na_position='last').reset_index()
    # print(df)
    fala.resposta(df["value"])


def conselho():
    api_url = "https://api.adviceslip.com/advice"  # Conselho
    data = requests.get(api_url)
    data_json = data.json()
    # print(data_json)
    df = json_normalize(data_json['slip'])
    fala.resposta(df['advice'])


def AteMais():
    Horario = int(datetime.datetime.now().hour)
    if Horario >= 0 and Horario < 12:
        fala.resposta('Tenha um ótimo dia')

    elif Horario >= 12 and Horario < 18:
        fala.resposta('Tenha uma ótima tarde')

    elif Horario >= 18 and Horario != 0:
        fala.resposta('Boa noite')


def projeto():
    perguntas = ['Qual o cliente?', 'Qual a cidade?', 'Qual o Nome do projeto']
    respostas = {}
    i = 0
    while i < len(perguntas):
        fala.resposta(perguntas[i])
        try:
            resp1 = ""
            resp2 = ""
            inicio = time.time()
            while int(len(resp1)) < 1:
                fim = time.time()
                if (fim - inicio) > timeOut:
                    # print(fim - inicio)
                    sons.SomRetorno()
                    resp2 = "não"
                    break
                resp1, _ = escuta.GivenCommand()
            if 'cancelar' in resp1:
                print('cancelar')
                break
            respostas[perguntas[i]] = resp1
            fala.resposta(f'{perguntas[i][7:-1]}: {resp1} está correto?')
            print(f'{perguntas[i][7:-1]}: {resp1} está correto?')

            inicio = time.time()
            while int(len(resp2)) < 1:
                fim = time.time()
                if (fim - inicio) > timeOut:
                    # print(fim - inicio)
                    sons.SomRetorno()
                    break
                resp2, _ = escuta.GivenCommand()
            if 'sim' in resp2:
                print('sim')
                i = i + 1
            elif 'não' in resp2:
                print('não')
                pass
            elif 'cancelar' in resp2:
                print('cancelar')
                break

        except:
            fala.resposta('Erro')
            fala.resposta('A conexão falhou')
    print(respostas)
    i = 0

