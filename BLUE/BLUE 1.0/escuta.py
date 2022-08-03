from vosk import Model, KaldiRecognizer
import speech_recognition as sr
import os
import pyaudio
import util
from nlu.classifier import classify



if not os.path.exists("/home/user/AGVS repository/BLUE/BLUE 1.0/vosk-model-pt-fb-v0.1.1-20220516_2113"):
    print ("Modelo em portugues nao encontrado.")
    exit (1)

if not os.path.exists("/home/user/AGVS repository/BLUE/BLUE 1.0/vosk-model-en-us-0.22-lgraph"):
    print ("Modelo em ingles nao encontrado.")
    exit (1)

model = Model("/home/user/AGVS repository/BLUE/BLUE 1.0/vosk-model-small-pt-0.3")
rec = KaldiRecognizer(model, 16000)

modelIng = Model("/home/user/AGVS repository/BLUE/BLUE 1.0/vosk-model-en-us-0.22-lgraph")
recIng = KaldiRecognizer(modelIng, 16000)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=(4096*2))
stream.start_stream()

#r = sr.Recognizer()

def GivenCommand():
    #if not util.check_internet():
    #print('vosk')
    data = stream.read(25000)
    rec.pause_threshold = 1
    rec.AcceptWaveform(data)
    recIng.pause_threshold = 1
    recIng.AcceptWaveform(data)
    try:
        Input = rec.Result().lower()
        for resp in Input.split('\n'):
            if 'text' in resp:
                pos = resp.find(":")
                comando = resp[pos+3:-1]
                print(comando)

        #Input = classify(comando)
        Input = comando
        InputIng = recIng.Result().lower()
    except:
        print('Não entendi, fale novamente')
        Input = None
        InputIng = None

    # else:
    #     print('google')
    #     try:
    #         with sr.Microphone() as s:
    #             r.adjust_for_ambient_noise(s)
    #             audio = r.listen(s)
    #             Input = r.recognize_google(audio, language="pt-BR").lower()
    #             InputIng = Input
    #     except:
    #         print('Não entendi, fale novamente')
    #         Input = None
    #         InputIng = None
    #
    return Input, InputIng