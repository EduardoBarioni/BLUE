import os


def dataset():
    path = "/home/user/AGVS repository/BLUE/BLUE 2.0/dataset"
    os.chdir(path)
    arquivos = []
    for i, file in enumerate(os.listdir()):
        if file.endswith(".yaml"):
            arquivos.append(file)

    ##Comando para juntar arquivos yaml
    #snips-nlu generate-dataset en dataset.yaml > dataset.json
    criaDataset = f"snips-nlu generate-dataset pt_br {' '.join(arquivos)} > dataset.json"
    #print(criaDataset)
    os.system(criaDataset)