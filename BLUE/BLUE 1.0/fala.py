import pyaudio
import pyttsx3
from plyer import notification

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
stream.start_stream()

speaker=pyttsx3.init()
speaker.setProperty('voice', 'pt+f1') #brazil-mbrola-3 #pt+m7
# voices = speaker.getProperty('voices')
# print(voices)
# speaker.setProperty('voice', voices[-1].id)
rate = speaker.getProperty('rate')
speaker.setProperty('rate', rate-50)

def resposta(audio):
    notification.notify(title = "B.L.U.E" ,message = audio ,timeout = 3)
    stream.stop_stream ()
    print('ASSISTENTE: ' + audio)
    speaker.say(audio)
    speaker.runAndWait()
    stream.start_stream ()

def notificar(textos):
    notification.notify(title = "B.L.U.E" ,message = textos ,timeout = 10)

def respostalonga(textofala):
    notification.notify(title = "B.L.U.E" ,message = textofala ,timeout = 30)
    stream . stop_stream ()
    speaker.say(textofala)
    speaker.runAndWait()
    stream . start_stream ()