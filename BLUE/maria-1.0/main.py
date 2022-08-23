#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer
import os
import pyaudio
import pyttsx3
import json
import core
from nlu.classifier import classify
import time
# Síntese de fala
engine = pyttsx3.init()
voices = engine.getProperty('voices')
#engine.setProperty('voice', voices[-2].id)
engine.setProperty('voice', 'pt+f4')

def speak(text):
    engine.say(text)
    engine.runAndWait()

def evaluate(text):
    #Reconhecer entidade do texto.
    entity = classify(text)

    #time
    if entity == 'time|getTime':
        speak(core.SystemInfo.get_time())
    elif entity == 'time|getDate':
        speak(core.SystemInfo.get_date())
    #Weather
    elif entity == 'weather|getWeather':
        speak(core.SystemInfo.get_Weather())
    #Open Abrir programas
    elif entity == 'open|notepad':
        speak('Abrindo o bloco de notas')
        os.system('notepad.exe')
    elif entity == 'open|chrome':
        speak('Abrindo o google chrome')
        os.system('"C:/Program Files/Google/Chrome/Application/chrome.exe"')


    #Cria projeto
    elif entity == 'NADA|NADA':
        speak('Criando projeto')
        pass

    elif entity == 'NADA|NADA':
        speak('Nada')
        pass




    print('Text: {}  Entity: {}'.format(text, entity))

# Reconhecimento de fala

model = Model('model')
rec = KaldiRecognizer(model, 16000)

modelIng = Model("modelIng")
recIng = KaldiRecognizer(modelIng, 16000)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=2048)
stream.start_stream()

# Loop do reconhecimento de fala
while True:

    data = stream.read(2048)
    if len(data) == 0:
        break

    if rec.AcceptWaveform(data):
        result = rec.Result()
        result = json.loads(result)
        text = result['text'].lower()
        print('entrou 01')
        if 'teste' in text:
            speak('Oi')
            inicio = time.time()
            print(text)
            while True:
                data = stream.read(2048)
                print('entrou 02')
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = rec.Result()
                    result = json.loads(result)
                    text = result['text']
                    if text is not '':
                        text = result['text']
                        print(text)
                        evaluate(text)
                        inicio = time.time()

                fim = time.time()
                if(fim - inicio) > 10:
                    print(fim - inicio)
                    #break
            