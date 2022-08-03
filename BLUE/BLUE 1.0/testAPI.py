import requests
import json
import pandas as pd
from pandas import json_normalize

def noticias():
    # api_url = "https://api.kanye.rest"  #

    # api_url = "https://newsapi.org/v2/top-headlines?sources=google-news-br&apiKey=b7c96fb430974e0a89860b1571b8286d" #Noticias
    # data = requests.get(api_url)
    # data_json = data.json()
    # if data_json['status'] == 'ok':
    #     print(data_json['totalResults'])
    #     for i in range(0, int(data_json['totalResults']), 1):
    #         print(f'---------------------------Noticia {i} -------------------------------------' )
    #         print(data_json['articles'][i]['source']['name'])
    #         print(data_json['articles'][i]['title'])
    #         print(data_json['articles'][i]['description'])

    api_url = "https://apinoticias.tedk.com.br/api/?q=parana&date=05/07/2022" #Noticias
    data = requests.get(api_url)
    data_json = data.json()
    print(data_json)
    df = json_normalize(data_json['list'])
    df = df.sort_values(by=['time'], ascending=False, na_position='last').reset_index()
    print(df)
    print(df["title"][0])

    # print(data_json)
    # if data_json['count'] > 0:
    #     print(data_json['count'])
    #     for i in range(0, int(data_json['count']), 1):
    #         print(f'---------------------------Noticia {i} -------------------------------------' )
    #         print(data_json['list'][i]['time'])
    #         print(data_json['list'][i]['title'])
    #         print(data_json['list'][i]['link'])



    #print(data_json)

def piadas():
    api_url = "https://api.chucknorris.io/jokes/random"  # Chuck Norris
    data = requests.get(api_url)
    data_json = data.json()
    #print(data_json)
    df = json_normalize(data_json)
    #df = df.sort_values(by=['value'], ascending=False, na_position='last').reset_index()
    #print(df)
    print(df["value"])

def conselhos():
    api_url = "https://api.adviceslip.com/advice"  # Conselho
    data = requests.get(api_url)
    data_json = data.json()
    #print(data_json)
    df = json_normalize(data_json['slip'])
    print(df['advice'])

def previsaodotempo():
    api_url = "https://api.hgbrasil.com/weather?key=d2e85270" #Previsão do tempo
    api_url = "https://api.hgbrasil.com/weather?key=d2e85270&user_ip=remote" #localizar pelo IP
    api_url = "https://api.hgbrasil.com/weather?key=d2e85270&city_name=curitiba"  # localizar pelo nome da cidade

    data = requests.get(api_url)
    data_json = data.json()
    print(data_json)
    df = json_normalize(data_json['results'])
    print(df)

def financeiro():
    api_url = "https://api.hgbrasil.com/finance?key=d2e85270"  # geral
    api_url = "https://api.hgbrasil.com/finance/stock_price?key=d2e85270&symbol=bidi4"  # IBOVESPA
    api_url = "https://api.hgbrasil.com/finance/stock_price?key=d2e85270&symbol=get-high"  # HIGH
    api_url = "https://api.hgbrasil.com/finance/stock_price?key=d2e85270&symbol=get-low"  # LOW


    data = requests.get(api_url)
    data_json = data.json()
    print(data_json)
    df = json_normalize(data_json['results'])
    print(df)
def localização():
    api_url = "https://api.hgbrasil.com/geoip?key=d2e85270&address=remote&precision=false"  # geral

    data = requests.get(api_url)
    data_json = data.json()
    print(data_json)
    df = json_normalize(data_json['results'])
    print(df)


#noticias()
#piadas()
#conselhos()
previsaodotempo()
#financeiro()
#localização()
