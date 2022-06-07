#!/usr/bin/env python
import rospy
import time
import rospkg
import sqlite3
from sqlite3 import Error
import math
import json


#variaveis globais
caminho = "";
bd_nome = "/AGVConfig.db";
pkg_nome = "banco_pk_zf"



###
def get_ControlMSG(nome):
    rota = []
    try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM ControleMSG where MSG = ?",(str(nome),))
            rows = cur.fetchall()
            for row in rows:
                                rota = {
                                  "MSG": row[0],
                                  "TAG": row[1],
                                  "Rota1":row[2],
                                  "Rota2":row[3],
                                  "Rota3":row[4],
                                  "Rota4":row[5],
                                  "Rota5":row[6],
                                  "Rota6":row[7],
                                  "Rota7":row[8],
                                  "Rota8":row[9],
                                  "Rota9":row[10],
                                  "Rota10":row[11]
                                  
                                }
            return rota
    except:
            return "Erro ao pegar ControlMSG"
    


def get_all_ControlMSG():
    rota = []
    try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM ControleMSG")
            rows = cur.fetchall()
            for row in rows:
                                #print(row[0])
                                rota += {
                                  "MSG": row[0],
                                  "Tag": row[1],
                                  "Rota1":row[2],
                                  "Rota2":row[3],
                                  "Rota3":row[4],
                                  "Rota4":row[5],
                                  "Rota5":row[6],
                                  "Rota6":row[7],
                                  "Rota7":row[8],
                                  "Rota8":row[9],
                                  "Rota9":row[10],
                                  "Rota10":row[11]
                                  
                                },
           
    except:
            return "Erro ao pegar ControlMSG"
    return rota


def get_status(nome):
    rota = 0
    try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Status where Nome = ?",(str(nome),))
            rows = cur.fetchall()
            rota = rows[0][0]
    except:
            return 0     
    return rota
             
def add_rotas(valor_id, Rota1, Rota2, Rota3, Rota4, Rota5, Rota6, Rota7, Rota8, Rota9, Rota10):
       # print(str(valor_id)+"  "+str(Rota1)+"  "+str(Rota2)+"  "+str(Rota3)+"  "+str(Rota4)+" "+str(Rota5)+" "+str(Rota6)+"  "+str(Rota7)+" "+str(Rota8)+" "+str(Rota9)+ " " +str(Rota10))
        try:
                sql = '''insert or replace into Rotas  (id, Rota1, Rota2, Rota3, Rota4, Rota5, Rota6, Rota7, Rota8, Rota9, Rota10)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
                cur = conn.cursor()
                cur.execute(sql, [valor_id, Rota1, Rota2, Rota3, Rota4, Rota5, Rota6, Rota7, Rota8, Rota9, Rota10])
                conn.commit()
                return 1
        except Exception as e: 
                return 0

                
def add_Tags_CMDS(valor_id, Tag1):
        try:
                sql = '''insert or replace into TagsCMDS  (id, Tag)
                     VALUES (?, ?)'''
                cur = conn.cursor()
                cur.execute(sql, [valor_id, Tag1])
                conn.commit()
                return 1
        except Exception as e: 
                return 0

                
def get_rota():
    rota = []
    try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Rotas WHERE id = ?",(1,))

            rows = cur.fetchall()
            for row in rows:

                       rota = {
                                  "Rota1":row[1],
                                  "Rota2":row[2],
                                  "Rota3":row[3],
                                  "Rota4":row[4],
                                  "Rota5":row[5],
                                  "Rota6":row[6],
                                  "Rota7":row[7],
                                  "Rota8":row[8],
                                  "Rota9":row[9],
                                  "Rota10":row[10]
                                  
                                },
                                
    except:
            print("Erro ao consultar rota")       
    return rota
    
def getControl():
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Controles")
        return cur.fetchall()
    except Exception as ex:
        print("Erro getControl: ")
        print(ex)
        return None

def getControlFromTag(idTag):
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Controles WHERE Tag = " + str(idTag))
        return cur.fetchall()
    except Exception as ex:
        print("Erro getControlFromTag: ")
        print(ex)
        return None

def set_nova_rota_inicial(idAGV, RotaInicial):
        #try:
                sql = '''UPDATE Configuracao set RotaInicial = ? WHERE idAGV = ?'''
                cur = conn.cursor()
                cur.execute(sql, [RotaInicial, idAGV])
                conn.commit()
                return 1
        #except Exception as e: 
       #         return 0


  
def get_configuracoes_agv():
    rota = []
    try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Configuracao")

            rows = cur.fetchall()
            for row in rows:

                       rota = {
                                  "idAGV":row[0],
                                  "RotaInicial":row[1]                                  
                                },
                                
    except:
            print("Erro ao consultar rota")             
    return rota

#subrota
def add_subrota(nome, tag_referencia, rotas_nome):
        try:
                sql = '''INSERT INTO subrotas  (nome, tag_referencia,rotas_nome)
                     VALUES (?,?,?)'''
                cur = conn.cursor()
                cur.execute(sql, [nome, tag_referencia, rotas_nome])
                conn.commit()
                return "OK!"
        except:
                return "Erro"
                
def update_subrota(nome, tag_referencia, rotas_nome, nome_antigo):
        try:
                 sql = '''UPDATE subrotas set nome = ?, tag_referencia = ?, rotas_nome = ? WHERE nome = ?'''
                 cur = conn.cursor()
                 cur.execute(sql, [nome, tag_referencia, rotas_nome, nome_antigo])
                 conn.commit()
                 return("OK!")
        except:
                 print("Erro ao atualizar subrota");                     
                 return("ERRO!")          

def get_subrota(param):
    subrota = []
    try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM subrotas WHERE nome = ?",(str(param),))

            rows = cur.fetchall()
           # print(rows)
            for row in rows:
                        subrota = {
                          "nome": row[0],
                          "tag_referencia": row[1],
                          "rotas_nome":row[2],
                          "nome_id": row[0]
                        }
            return subrota
    except:
            print("Erro ao consultar ponto")
    return subrota
    
    
    
def get_subrota_rota(param):
    subrota = []
    try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM subrotas WHERE rotas_nome = ?",(str(param),))
            rows = cur.fetchall()
            for row in rows:
                        subrota += {
                          "nome": row[0],
                          "tag_referencia": row[1],
                          "rotas_nome":row[2],
                          "nome_id": row[0]
                        },
    except:
            print("Erro ao consultar rotas_nome")
    return subrota
    
    
def get_subrotas():
    subrotas = []
    try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM subrotas")

            rows = cur.fetchall()
            print(rows)
            for row in rows:
                        subrotas += {
                          "nome": row[0],
                          "tag_referencia": row[1],
                          "rotas_nome":row[2],
                          "nome_id": row[0]
                        },

    except:
            print("Erro ao consultar ponto")
    return subrotas

def delete_subota(param):
        try:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM subrotas WHERE nome = ?",(str(param),))
                    conn.commit()
                    return "OK!"
        except:
                    return "Erro!"
                
        
#ponto                
def add_ponto(nome, posX, posY, posZ, angulo, frame, Importante, Comandos, subrota_nome):
        try:
                sql = '''INSERT INTO pontos  (nome, posX, posY, posZ, angulo, frame, Importante, Comandos, subrota_nome)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
                cur = conn.cursor()
                cur.execute(sql, [nome, posX, posY, posZ, angulo, frame, Importante, Comandos, subrota_nome])
                conn.commit()
                return 1
        except Exception as e: 
                return 0

def update_ponto(nome, posX, posY, posZ, angulo, frame, Importante, Comandos, subrota_nome, nome_antigo):
        try:
                 sql = '''UPDATE pontos set  nome = ?, posX = ?, posY = ?, posZ = ?, angulo = ?, frame = ?, Importante = ?, Comandos = ?, subrota_nome = ? WHERE nome = ?'''
                 cur = conn.cursor()
                 cur.execute(sql, [nome, posX, posY, posZ, angulo, frame, Importante, Comandos, subrota_nome, nome_antigo])
                 conn.commit()
                 return("OK!")
        except:
                 print("Erro ao atualizar ponto");
                 return("Erro!")
      
def get_ponto(nome):
    ponto = []
    try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM pontos WHERE nome = ?",(str(nome),))

            rows = cur.fetchall()
            for row in rows:
                        ponto = {
                          "nome": row[0],
                          "posX": row[1],
                          "posY": row[2],
                          "posZ": row[3],
                          "angulo": row[4],
                          "frame":  row[5],
                          "Importante": row[6],
                          "Comandos":  row[7],
                          "subrota_nome": row[8],
                          "nome_id": row[0]
                        }
            return ponto
    except:
            print("Erro ao consultar ponto")
    return ponto
    

def get_pontos():
    pontos = []
    try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM pontos")

            rows = cur.fetchall()
            for row in rows:
                        pontos += {
                          "nome": row[0],
                          "posX": row[1],
                          "posY": row[2],
                          "posZ": row[3],
                          "angulo": row[4],
                          "frame":  row[5],
                          "Importante": row[6],
                          "Comandos":  row[7],
                          "subrota_nome": row[8],
                          "nome_id": row[0]
                        },
    except:
            print("Erro ao consultar ponto")
    return pontos
    
    


def get_cont_pontos():
    rows = []
    try:
            cur = conn.cursor()
            cur.execute("select COUNT(*) from pontos")
            rows = cur.fetchall()
            return rows[0][0]
    except:
            print("Erro ao consultar ponto")
            return 0

def get_pontos_sub_rota(param):
    pontos = []
    try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM pontos WHERE subrota_nome = ?",(str(param),))

            rows = cur.fetchall()
            for row in rows:
                        pontos += {
                          "nome": row[0],
                          "posX": row[1],
                          "posY": row[2],
                          "posZ": row[3],
                          "angulo": row[4],
                          "frame":  row[5],
                          "Importante": row[6],
                          "Comandos":  row[7],
                          "subrota_nome": row[8],
                          "nome_id": row[0]
                        },
    except:
            print("Erro ao consultar ponto")
    return pontos

def delete_ponto(param):
        try:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM pontos WHERE nome = ?",(str(param),))
                    conn.commit()
                    return "OK!"
        except:
                    return "Erro!"
                    


def getCarregadores():
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Carregadores")
        return cur.fetchall()
    except Exception as ex:
        print("Erro getCarregadores: " + str(ex))
    
def getCarregadorFromTag(idTag):
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Carregadores WHERE Tag = " + str(idTag))
        return cur.fetchall()
    except Exception as ex:
        print("Erro getCarregadorFromTag: ")
        print(ex)
        return None

def cria_tabelas():

        sql_rotas = """ CREATE TABLE IF NOT EXISTS rotas (
                                        nome text PRIMARY KEY
                                    ); """
                                    
        sql_subrotas = """ CREATE TABLE IF NOT EXISTS subrotas (
                                        nome text PRIMARY KEY,
                                        tag_referencia integer,
                                        rotas_nome text,
                                        FOREIGN KEY (rotas_nome) REFERENCES rotas (nome) 
                                    ); """
                                    
        sql_pontos = """ CREATE TABLE IF NOT EXISTS pontos (
                                        nome text PRIMARY KEY,
                                        posX REAL,
                                        posY REAL,
                                        posZ REAL,
                                        angulo REAL,
                                        frame text NOT NULL,
                                        Importante integer NOT NULL,
                                        Comandos text,
                                        subrota_nome text,
                                        FOREIGN KEY (subrota_nome) REFERENCES subrotas (nome) ON DELETE CASCADE 
                                    ); """
         # create tables
        if conn is not None:
                # create projects table
                create_table(conn, sql_rotas)
                create_table(conn, sql_subrotas)
                create_table(conn, sql_pontos)

        else:
                print("Error! cannot create the database connection.")
                

def remove_tabelas():
        sql_rotas = """ DROP TABLE rotas; """                            
        sql_subrotas = """ DROP TABLE subrotas; """                           
        sql_pontos = """DROP TABLE pontos;"""
         # create tables
        if conn is not None:
                # create projects table
                create_table(conn, sql_rotas)
                create_table(conn, sql_subrotas)
                create_table(conn, sql_pontos)
        else:
                print("Error! cannot drop the database connection.")
                return "Erro!"
        return "Ok"


####Banco de dados
def create_connection(db_file):

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn   

def create_table(conn, create_table_sql):

    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def conecta_bd():
        global conn;
        rospack = rospkg.RosPack()
        rate = rospy.Rate(10)
        # list all packages, equivalent to rospack list
        rospack.list() 
        caminho = rospack.get_path(pkg_nome)
        caminho = caminho+(bd_nome);
        conn = create_connection(caminho)
       # cria_tabelas()
        return caminho





        

 

	

	

