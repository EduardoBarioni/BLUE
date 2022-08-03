import speech_recognition as sr
from gtts import gTTS
from playsound import playsound

#Funcao responsavel por falar
def cria_audio(audio):
    tts = gTTS(audio,lang='pt-br')
    #Salva o arquivo de audio
    tts.save('audio.mp3')
    print("audio gravado")
    #Da play ao audio
    playsound('hello.mp3')

