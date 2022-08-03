'''
    Description:
    Play music on Spotify with python.
    Author: AlejandroV
    Version: 1.0
    Video: https://youtu.be/Vj64pkXtz28
'''
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import webbrowser as web
import pyautogui
from time import sleep

# your credentials
client_id = '8700e1c7ed5540c9b159c4260dd43a3f'
client_secret = '87198a5a325b4bf8ae97d617d4d019c4'
flag = 0

# artist and name of the song
author = 'vintage cuture'
song = 'free'

if len(author) > 0:
    # authenticate
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id, client_secret))
    result = sp.search(author)
    print(result["tracks"])

    for i in range(0, len(result["tracks"]["items"])):
        # songs by artist
        # name_song = result["tracks"]["items"][i]["name"].upper()
        # print(name_song)
        nome_artista = result['tracks']['items'][0]['artists'][0]['name']
        nome_musica = result['tracks']['items'][0]['name'].upper()
        track_uri = result['tracks']['items'][0]['uri']

        print(nome_artista)
        print(nome_musica)
        print(track_uri)
        #sp.start_playback(uris=[track_uri])
        #
        # if song in name_song:
        #     flag = 1
        #
        #     web.open(result["tracks"]["items"][i]["uri"])
        #     sleep(5)
        #     pyautogui.press("enter")
        #     break

# # if song by artist not found
# if flag == 0:
#     song = song.replace(" ", "%20")
#     web.open(f'spotify:search:{song}')
#     sleep(5)
#     for i in range(18):
#         pyautogui.press("tab")
#
#     for i in range(2):
#         pyautogui.press("enter")
#         sleep(1)
