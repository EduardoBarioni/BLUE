#!/usr/bin/env python

import sqlite3
import rospkg


#Dados do banco
caminho = "";
bd_nome = "/AGVConfig.db";
pkg_nome = "banco_pk_zf"

conn = None

#Conexão-----------------------------------------------------------------
def create_connection(db_file):
    global conn;
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn   


def conecta_bd():
        global conn;

        rospack = rospkg.RosPack()
        # list all packages, equivalent to rospack list
        rospack.list() 
        caminho = rospack.get_path(pkg_nome)
        caminho = caminho+(bd_nome);
        conn = create_connection(caminho)

def closeConn():
    try:
        conn.close()
    except:
        pass
        
#-----------------------------------------------------------------------

#Funcoes genericas------------------------------------------------------
def getAllItems(tabela):
    try:
        #rospack = rospkg.RosPack()
        #rospack.list()
        #caminho = rospack.get_path(pkg_nome)
        #caminho = caminho+(bd_nome)
        #with sqlite3.connect(caminho) as con:
        conecta_bd()
        mycursor = conn.cursor()
        sql_select = "SELECT * FROM " + tabela
        mycursor.execute(sql_select)
        result = mycursor.fetchall()
        return result  
    except Exception as ex:
        print("Erro getAll: ")
        print(ex)
        return None

def getItem(tabela, item, valor):
    try:
        conecta_bd()
        mycursor = conn.cursor()
        sql_select = "SELECT * FROM " + tabela + " WHERE " + item + " = \"" + valor + "\""
        #print(sql_select)
        mycursor.execute(sql_select)
        return mycursor.fetchall()  
    except Exception as ex:
        print("Erro getItem: ")
        print(ex)
        return None

def getItem2(tabela, item1, valor1, item2, valor2):
    try:
        conecta_bd()
        mycursor = conn.cursor()
        sql_select = "SELECT * FROM " + tabela + " WHERE " + item1 + " = \"" + valor1 + " \" AND " + item2 + " = \"" + valor2 + "\""
        #print(sql_select)
        mycursor.execute(sql_select)
        return mycursor.fetchall()  
    except Exception as ex:
        print("Erro getItem2: ")
        print(ex)
        return None
        
def getFuncoes(valor1, valor2):
    try:
        conecta_bd()
        mycursor = conn.cursor()
        #sql_select = "SELECT * FROM " + tabela + " WHERE " + item1 + " = \"" + valor1 + " \" AND " + item2 + " = \"" + valor2 + "\""
        sql_select = " SELECT * FROM Funcoes WHERE (Rota = 0 or Rota = \"" + valor1 + " \") AND IdPontosPosicao = \" " + valor2 + "\""  
        #print(sql_select)
        mycursor.execute(sql_select)
        return mycursor.fetchall()  
    except Exception as ex:
        print("Erro getFuncoes: ")
        print(ex)
        return None
    
def updateItem(tabela, coluna, novoValor, comparar1, comparar2):
    try:
        rospack = rospkg.RosPack()
        rospack.list()
        caminho = rospack.get_path(pkg_nome)
        caminho = caminho+(bd_nome)
        with sqlite3.connect(caminho) as con:
            #conecta_bd()
            mycursor = con.cursor()
            sql_update = "UPDATE " + tabela + " SET " + coluna + " = \"" + novoValor + "\" WHERE " + comparar1 + " = " + comparar2
            mycursor.execute(sql_update)
            con.commit()
            #conn.close() 
    except Exception as ex:
        print("Erro updateItem: ")
        print(ex)
        
def getMax(tabela, coluna):
    try:
        rospack = rospkg.RosPack()
        rospack.list()
        caminho = rospack.get_path(pkg_nome)
        caminho = caminho+(bd_nome)
        with sqlite3.connect(caminho) as con:
            #conecta_bd()
            mycursor = con.cursor()
            sql_max = "SELECT MAX("  + str(coluna) + ") FROM " + str(tabela) 
            mycursor.execute(sql_max)  
            return mycursor.fetchall()
            #conn.close() 
    except Exception as ex:
        print("Erro getMax: ")
        print(ex)

def getMin(tabela, coluna):
    try:
        rospack = rospkg.RosPack()
        rospack.list()
        caminho = rospack.get_path(pkg_nome)
        caminho = caminho+(bd_nome)
        with sqlite3.connect(caminho) as con:
            #conecta_bd()
            mycursor = con.cursor()
            sql_min = "SELECT MIN("  + str(coluna) + ") FROM " + str(tabela) 
            mycursor.execute(sql_min)  
            return mycursor.fetchall()
            #conn.close() 
    except Exception as ex:
        print("Erro getMax: ")
        print(ex)

def deleteAllItems(tabela):
    try:
        rospack = rospkg.RosPack()
        rospack.list()
        caminho = rospack.get_path(pkg_nome)
        caminho = caminho+(bd_nome)
        with sqlite3.connect(caminho) as con:
            mycursor = con.cursor()
            sql_delete = "DELETE FROM " + str(tabela) 
            mycursor.execute(sql_delete)
            con.commit()
    except Exception as ex:
        print("Erro deletando entradas: " + str(ex))
 
#---------------------------------------------------------------------        

#Funcoes especificas--------------------------------------------------
def insertTagVirtual(idTag, acao1, acao2, acao3, acao4, acao5, 
    acao6, acao7, acao8, acao9, acao10, rotas1, rotas2, rotas3, rotas4, rotas5,
    rotas6, rotas7, rotas8, rotas9, rotas10):
    #print("ID: " + idTag)
    #print("Acao1: " + acao1)
    #print("Acao2: " + acao2)
    #print("Acao3: " + acao3)
    #print("Acao4: " + acao4)
    #print("Acao5: " + acao5)
    #print("Acao6: " + acao6)
    #print("Acao7: " + acao7)
    #print("Acao8: " + acao8)
    #print("Acao9: " + acao9)
    #print("Acao10: " + acao10)
    #print("Rotas1: " + rotas1)
    #print("Rotas2: " + rotas2)
    #print("Rotas3: " + rotas3)
    #print("Rotas4: " + rotas4)
    #print("Rotas5: " + rotas5)
    #print("Rotas6: " + rotas6)
    #print("Rotas7: " + rotas7)
    #print("Rotas8: " + rotas8)
    #print("Rotas9: " + rotas9)
    #print("Rotas10: " + rotas10)
    try:
        conecta_bd()
        mycursor = conn.cursor()
        sql_insert = '''INSERT OR REPLACE INTO TagVirtual ("Tag", "Virtual", "Acao1", "Acao2", "Acao3",
         "Acao4", "Acao5", "Acao6", "Acao7", "Acao8", "Acao9", "Acao10", "Rota1", "Rota2", "Rota3", "Rota4", "Rota5",
         "Rota6", "Rota7", "Rota8", "Rota9", "Rota10") values (?,0,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
        mycursor.execute(sql_insert, [idTag, acao1, acao2, acao3, acao4, acao5, acao6, acao7, acao8, acao9, acao10, 
        rotas1, rotas2, rotas3, rotas4, rotas5, rotas6, rotas7, rotas8, rotas9, rotas10])
        conn.commit()
        conn.close()
    except Exception as ex:
        print("Erro insertTagVirtual: ")
        print(ex)

def insertTagsPosicao(idTag, virtual, pos, rota, proxTag):
    try:
        conecta_bd()
        mycursor = conn.cursor()
        sql_insert = '''INSERT OR REPLACE INTO TagsPosicao ("idTag", "TagVirtual", "Posicao", "Rota", "ProximaTag") 
        values (?, ?, ?, ?, ?)'''
        mycursor.execute(sql_insert, [idTag, virtual, pos, rota, proxTag])
        conn.commit()
        conn.close()
    except Exception as ex:
        print("Erro insertTagsPosicao: ")
        print(ex)

def insertOffsets(id_n, offset_x, offset_y, offset_yaw):
    try:
        conecta_bd()
        mycursor = conn.cursor()
        sql_insert = '''INSERT OR REPLACE INTO ZeraErro ("ID", "X", "Y", "Yaw") 
        values (?, ?, ?, ?)'''
        mycursor.execute(sql_insert, [id_n, offset_x, offset_y, offset_yaw])
        conn.commit()
        conn.close()
    except Exception as ex:
        print("Erro insertOffsets: ")
        print(ex)
    
def getTagsPosicao(idTag, rota_atual):
    try:
        conecta_bd()
        mycursor = conn.cursor()
        mycursor.execute("SELECT * FROM TagsPosicao WHERE idTag = ? AND Rota = ?",(str(idTag), str(rota_atual),))
        return mycursor.fetchall()
    except Exception as ex:
        print("Erro getTagsPosicao: ")
        print(ex)
        

def insertTagsPerdidas(idTag, qntd):
    conecta_bd()
    mycursor = conn.cursor()
    sql_insert = '''INSERT INTO TagsPerdidas ("Tag", "Quantidade") values (?, ?)'''
    mycursor.execute(sql_insert, [idTag, qntd])
    conn.commit()
    conn.close()
    
def incrementQntdPerdidas(idTag):
    try:
        conecta_bd()
        mycursor = conn.cursor()
        sql_update = "UPDATE TagsPerdidas SET Quantidade = Quantidade + 1 WHERE Tag = " + str(idTag)
        mycursor.execute(sql_update)
        conn.commit()
        #conn.close() 
    except Exception as ex:
        print("Erro incrementQntdPerdidas: ")
        print(ex)
    
def insertPontosPosicao(ID, pos_x, pos_y, funcoes, prox_ID):
    try:
        rospack = rospkg.RosPack()
        rospack.list()
        caminho = rospack.get_path(pkg_nome)
        caminho = caminho+(bd_nome)
        with sqlite3.connect(caminho) as con:
            #conecta_bd()
            mycursor = con.cursor()
            sql_insert = '''INSERT OR REPLACE INTO PontosPosicao ("ID", "Pos_X", "Pos_Y", "Funcao", "ProxID") 
            values (?, ?, ?, ?, ?)'''
            mycursor.execute(sql_insert, [ID, pos_x, pos_y, funcoes, prox_ID,])  
            con.commit()
            #conn.close() 
    except Exception as ex:
        print("Erro insertPontosPosicao: ")
        print(ex)
 
 
def deleteItem(tabela, item, valor):
    try:
        rospack = rospkg.RosPack()
        rospack.list()
        caminho = rospack.get_path(pkg_nome)
        caminho = caminho+(bd_nome)
        with sqlite3.connect(caminho) as con:
            mycursor = con.cursor()
            sql_delete = "DELETE FROM " + str(tabela) + " WHERE " + str(item) + " = " + str(valor)
            mycursor.execute(sql_delete)
            con.commit()
    except Exception as ex:
        print("Erro deletando entrada: " + str(ex))
 


#---------------------------------------------------------------------


    

'''
try:
    mycursor = conn.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS iluminacao (estado VARCHAR(255) PRIMARY KEY, vermelho INT, verde INT, azul INT, tipo VARCHAR(255), tempo INT)")
    sql_iluminacao = "INSERT INTO iluminacao (estado, vermelho, verde, azul, tipo, tempo ) VALUES (?, ?, ?, ?, ?, ?)"
    val_iluminacao = [
        ("Emergencia",  100, 0, 0, "aceso", 0),
        ("Carregando", 40, 40, 40, "oscilando", 100),
        ("Bateria Critica", 100, 0, 0, "1", 1000),
        ("Manual", 0, 0, 0, "aceso", 0), #Como as intensidades são todas 0, fica apagado
        ("Parado", 0, 0, 100, "1", 0),
        ("Desconectado", 100, 0, 0, "5", 200),
        ("Sem Rota", 40, 0, 0, "oscilando", 100),
        ("Fuga de Rota", 100, 0, 0, "4", 200),
        ("Obstaculo Interno", 100, 0, 0, "aceso", 0),
        ("Obstaculo Intermediario", 100, 0, 0, "aceso", 0),
        ("Obstaculo Externo", 100, 0, 0, "aceso", 0),
        ("Navegando", 0, 0, 100, "aceso", 100)
    ]

    mycursor.executemany(sql_iluminacao, val_iluminacao)
    conn.commit()
except Exception as ex:
    print("Erro iluminacao: ")
    print(ex)

try:
    mycursor = conn.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS som (estado VARCHAR(255) PRIMARY KEY, buzina INT, buzzer INT)")
    sql_som = "INSERT INTO som (estado, buzina, buzzer) VALUES (?, ?, ?)"
    val_som = [
        ("Emergencia",  0, 0),
        ("Carregando", 0, 0),
        ("Bateria Critica", 0, 0),
        ("Manual", 0, 0), 
        ("Parado", 0, 0),
        ("Desconectado", 0, 0),
        ("Sem Rota", 0, 0),
        ("Fuga de Rota", 0, 0),
        ("Obstaculo Interno", 0, 0),
        ("Obstaculo Intermediario", 0, 0),
        ("Obstaculo Externo", 0, 0),
        ("Navegando", 0, 0)
    ]

    mycursor.executemany(sql_som, val_som)
    conn.commit()
except Exception as ex2:
    print("Erro som: ")
    print(ex2)  

try:
    mycursor = conn.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS dados (AGV VARCHAR(255), rota INT, tag_anterior VARCHAR(255), tag_atual VARCHAR(255), posicao FLOAT, media_erro FLOAT, variacao_tempo_erro FLOAT)")

    conn.commit()
    conn.close()
except Exception as ex3:
    print("Erro dados: ")
    print(ex3)  
    conn.close()      


def Alterar_entrada(tabela, estado, coluna, valor):
    conn = sqlite3.connect(database)
    mycursor = conn.cursor()
    sql_alterar = "UPDATE %s SET %s = %s WHERE estado = %s"
    sql_valores = (tabela, coluna, valor, estado)
    mycursor.execute(sql_alterar, sql_valores)
    conn.commit()
    conn.close()


def Dados_iluminacao():
    conn = sqlite3.connect(database)
    mycursor = conn.cursor()
    mycursor.execute("SELECT * FROM iluminacao")
    return mycursor.fetchall()   

def Dados_som():
    conn = sqlite3.connect(database)
    mycursor = conn.cursor()
    mycursor.execute("SELECT * FROM som")
    return mycursor.fetchall()

'''

