import json
from datetime import date
from util import temperaturadacpu, cpu, bateria, datahoje, horario, previsaodotempo, matematica, noticias, openMediaPipe, openYolo

def comando(Input):

    #print(Input)
    #print(json.dumps(Input, indent=2))

    #Cria a lista de comandos
    inf = ['0', '0', '0', '0', '0']
    #Identifica qual a intenção
    try:
        inf[0] = Input['intent']['intentName']
        inf[1] = Input['intent']['probability']
    except:
        #print("sem comandos")
        pass

    #Identifica os slots
    try:
        # Horario
        if 'verificarHora' in inf[0]:
            horario()

        # Data
        if 'verificarData' in inf[0]:
            datahoje()

        # Bateria
        if 'statusBateria' in inf[0]:
            bateria()

        # Processamento da CPU
        if 'utilizacaoCPU' in inf[0]:
            cpu()

        # Temperatura da CPU
        if 'tempCPU' in inf[0]:
            temperaturadacpu()

        # Previsão do tempo
        if 'verificarClima' in inf[0]:

            for i, slot in enumerate(Input['slots']):
                # print(f'clima {i}')
                if 'local' in Input['slots'][i]['slotName']:
                    inf[2] = Input['slots'][i]['value']['value']
                elif 'date' in Input['slots'][i]['slotName']:
                    inf[3] = Input['slots'][i]['value']['value']

            # print(f"Origem: {inf[2]}")
            # print(f"Data: {inf[3]}")

            previsaodotempo(inf[2], inf[3])

        #Calculadora
        if 'realizaCalculo' in inf[0]:

            for i, slot in enumerate(Input['slots']):
                if 'parcela01' in Input['slots'][i]['slotName']:
                    inf[2] = Input['slots'][i]['value']['value']
                elif 'conta' in Input['slots'][i]['slotName']:
                    inf[3] = Input['slots'][i]['value']['value']
                elif 'parcela02' in Input['slots'][i]['slotName']:
                    inf[4] = Input['slots'][i]['value']['value']
            matematica(inf[2], inf[4], inf[3])

        #Procurar noticias
        if 'procuraNoticias' in inf[0]:
            noticias()
            # for i, slot in enumerate(Input['slots']):
            #     if 'local' in Input['slots'][i]['slotName']:
            #         inf[2] = Input['slots'][i]['value']['value']
            #     elif 'date' in Input['slots'][i]['slotName']:
            #         inf[3] = Input['slots'][i]['value']['value']
            #     elif 'numero' in Input['slots'][i]['slotName']:
            #         inf[4] = Input['slots'][i]['value']['value']

        #Compra de passagens
        if 'procurarVoo' in inf[0]:
            for i, slot in enumerate(Input['slots']):
                if 'origem' in Input['slots'][i]['slotName']:
                    inf[2] = Input['slots'][i]['value']['value']
                elif 'destino' in Input['slots'][i]['slotName']:
                    inf[3] = Input['slots'][i]['value']['value']
                elif 'date' in Input['slots'][i]['slotName']:
                    inf[4] = Input['slots'][i]['value']['value']
            # print(inf)
            # print(f"Origem: {inf[2]}")
            # print(f"Destino: {inf[3]}")
            # print(f"Data: {inf[4]}")

        #Comando de gestos
        if 'OpenMediaPipe' in inf[0]:
            openMediaPipe()
            # for i, slot in enumerate(Input['slots']):
            #     if 'origem' in Input['slots'][i]['slotName']:
            #         inf[2] = Input['slots'][i]['value']['value']
            #     elif 'destino' in Input['slots'][i]['slotName']:
            #         inf[3] = Input['slots'][i]['value']['value']
            #     elif 'date' in Input['slots'][i]['slotName']:
            #         inf[4] = Input['slots'][i]['value']['value']

        #Reconhecimento de objetos/pessoas
        if 'OpenYolo' in inf[0]:
            openYolo()
            # for i, slot in enumerate(Input['slots']):
            #     if 'origem' in Input['slots'][i]['slotName']:
            #         inf[2] = Input['slots'][i]['value']['value']
            #     elif 'destino' in Input['slots'][i]['slotName']:
            #         inf[3] = Input['slots'][i]['value']['value']
            #     elif 'date' in Input['slots'][i]['slotName']:
            #         inf[4] = Input['slots'][i]['value']['value']
    except:
        print("Não foi possivel entender")