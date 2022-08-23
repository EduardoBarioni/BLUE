import datetime
import requests

class SystemInfo:
    def __init__(self):
        pass

    @staticmethod
    def get_time():
        now = datetime.datetime.now()
        answer = 'São {} horas e {} minutos.'.format(now.hour, now.minute)
        return answer

    @staticmethod
    def get_date():
        now = datetime.datetime.now()
        answer = 'Hoje é dia {} de {} de {}'.format(now.day, now.strftime("%B"), now.year)
        return answer

    @staticmethod
    def get_Weather():
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
                    answer = 'Erro. Não foi possivel verificar o clima. Tente outra vez o comando'
                else:
                    answer = 'Verificando clima para a cidade de {}. O clima hoje está {}. A temperatura é de  {}°. O vento está em {} kilometros por hora e a umidade é de {}%'.format(data_json['name'], dicionario[tipoclima], tempint, ventoint, str(main['humidity']))

        except:
            answer = 'Erro na conexão. Tente novamente o comando'
        return answer