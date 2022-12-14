#!/usr/sbin/python3
# -*- coding: utf-8 -*-
from random import randint
import socket
import multiprocessing as mp
import _thread
import json
import string
import sys
import os


class Node:
    def __init__(self, ip):
        self._inicializado = False
        self.ip = ip
        self.id = hash(f"{ip}+rafael")
        self.porta = 12345
        self.sucessor = {}
        self.antecessor = {}


class ServidorP2P:
    def __init__(self, ip=None) -> None:
        self.node = Node(ip=sys.argv[1])
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__t1 = _thread.start_new_thread(self.controle, ())
        self.interface()

    def controle(self) -> None:
        print(f"=> Iniciando P2P Server (ip={self.node.ip}, porta={self.node.porta})")
        orig = ("", self.node.porta)
        self.udp.bind(orig)

        while True:
            msg, cliente = self.udp.recvfrom(1024)
            msg_decoded = msg.decode("utf-8")
            string_dict = json.loads(msg_decoded)
            if string_dict["codigo"] == 0:
                print("pegando pelo metodo join o sucessor e antecessor do no que vamos inserir")
                dest = (cliente)#duvida aqui, cliente ja tem o ip e a porta?
                msg = {}
                msg["codigo"] = 64
                msg["id_sucessor"] = self.node.id
                msg["ip_sucessor"] = self.node.ip
                msg["id_antecessor"] = self.node.antecessor["id"]
                msg["ip_antecessor"] = self.node.antecessor["ip"]
                string_json = json.dumps(msg)
                self.udp.sendto(string_json.encode('utf-8'), dest)
            elif string_dict["codigo"] == 1:
                if self.node.antecessor["id"] == string_dict["identificador"]:
                    self.node.antecessor["id"] = string_dict["id_antecessor"]
                    self.node.antecessor["ip"] = string_dict["ip_antecessor"]     
                else:
                    self.node.sucessor["id"] = string_dict["id_sucessor"]
                    self.node.sucessor["ip"] = string_dict["ip_sucessor"]
                    dest = (cliente)
                    msg = {}
                    msg["codigo"] = 65
                    msg["id_antecessor"] = self.node.id
                    string_json = json.dumps(msg)
                    self.udp.sendto(string_json.encode('utf-8'), dest)
            elif string_dict["codigo"] == 2:
                if self.node.id == self.node.sucessor["id"]:
                    print("Fazendo Lookup")
                    dest = (string_dict["ip_origem_busca"], self.node.porta)
                    msg = {}
                    msg['codigo'] = 66
                    msg['id_busca'] = string_dict['id_busca']
                    msg['id_origem'] = string_dict['id_busca']
                    msg['ip_origem'] = string_dict['ip_origem_busca']
                    msg['id_sucessor'] = self.node.sucessor['id']
                    msg['ip_sucessor'] = self.node.sucessor['ip']
                    string_json = json.dumps(msg)
                    self.udp.sendto(string_json.encode('utf-8'), dest)
                elif string_dict['id_busca'] > self.node.id and string_dict['id_busca'] > self.node.sucessor["id"]: 
                    dest = (self.node.sucessor["ip"], self.node.porta)
                    msg = {}
                    msg["codigo"] = 2
                    msg["identificador"] = string_dict["id_busca"]
                    msg["ip_origem_busca"] = string_dict["ip_origem_busca"]
                    msg["id_busca"] = string_dict["id_busca"]
                    string_json = json.dumps(msg)
                    self.udp.sendto(string_json.encode('utf-8'), dest)
                elif string_dict['id_busca'] > self.node.id and string_dict['id_busca'] < self.node.sucessor['id']:
                    dest = (string_dict["ip_origem_busca"], self.node.porta)
                    msg = {}
                    msg['codigo'] = 66
                    msg['id_busca'] = string_dict['id_busca']
                    msg['id_origem'] = string_dict['id_busca']
                    msg['ip_origem'] = string_dict['ip_origem_busca']
                    msg['id_sucessor'] = self.node.sucessor['id']
                    msg['ip_sucessor'] = self.node.sucessor['ip']
                    string_json = json.dumps(msg)
                    self.udp.sendto(string_json.encode('utf-8'), dest)
                elif string_dict['id_busca'] < self.node.id and string_dict['id_busca'] > self.node.antecessor["id"]:
                    dest = (string_dict["ip_origem_busca"], self.node.porta)
                    msg = {}
                    msg['codigo'] = 66
                    msg['id_busca'] = string_dict['id_busca']
                    msg['id_origem'] = string_dict['id_busca']
                    msg['ip_origem'] = string_dict['ip_origem_busca']
                    msg['id_sucessor'] = self.node.id
                    msg['ip_sucessor'] = self.node.ip
                    string_json = json.dumps(msg)
                    self.udp.sendto(string_json.encode('utf-8'), dest)
                elif self.node.id > self.node.sucessor["id"]:
                    dest = (string_dict["ip_origem_busca"], self.node.porta)
                    msg = {}
                    msg['codigo'] = 66
                    msg['id_busca'] = string_dict['id_busca']
                    msg['id_origem'] = string_dict['id_busca']
                    msg['ip_origem'] = string_dict['ip_origem_busca']
                    msg['id_sucessor'] = self.node.sucessor['id']
                    msg['ip_sucessor'] = self.node.sucessor['ip']
                    string_json = json.dumps(msg)
                    self.udp.sendto(string_json.encode('utf-8'), dest)
                else:
                    dest = (self.node.sucessor["ip"], self.node.porta)
                    msg = {}
                    msg["codigo"] = 2
                    msg["identificador"] = string_dict["id_busca"]
                    msg["ip_origem_busca"] = string_dict["ip_origem_busca"]
                    msg["id_busca"] = string_dict["id_busca"]
                    string_json = json.dumps(msg)
                    self.udp.sendto(string_json.encode('utf-8'), dest)
                    print("pode ocorrer loop")
                

            elif string_dict["codigo"] == 3:
                if "id_novo_sucessor" in string_dict.keys():
                    self.node.sucessor = {"id": string_dict["id_novo_sucessor"], "ip": string_dict["ip_novo_sucessor"]}
                    print("N?? antecessor atualizado com update")
                else:
                    self.node.antecessor = {"id": string_dict["id_novo_antecessor"], "ip": string_dict["ip_novo_antecessor"]}
                    print("N?? sucessor atualizado com update")
                    dest = (cliente)
                    msg = {}
                    msg["codigo"] = 67
                    msg["id_antecessor"] = self.node.id
                    string_json = json.dumps(msg)
                    self.udp.sendto(string_json.encode('utf-8'), dest)
                
                
            elif string_dict["codigo"] == 64:
                self.node.antecessor["id"] = string_dict["id_antecessor"]
                self.node.antecessor["ip"] = string_dict["ip_antecessor"]
                self.node.sucessor["id"] = string_dict["id_sucessor"]
                self.node.sucessor["ip"] = string_dict["ip_sucessor"]
                print("Setado o antecessor e sucessor do novo no, hora do update dos seus n??s vizinhos")

                dest = (self.node.antecessor["ip"], self.node.porta)
                msg = {}
                msg['codigo'] = 3
                msg['identificador'] = self.node.id
                msg['id_novo_sucessor'] = self.node.id 
                msg['ip_novo_sucessor'] = self.node.ip
                string_json = json.dumps(msg)
                self.udp.sendto(string_json.encode('utf-8'), dest)

                dest = (self.node.sucessor["ip"], self.node.porta)
                msg = {}
                msg['codigo'] = 3
                msg['identificador'] = self.node.id
                msg['id_novo_antecessor'] = self.node.id 
                msg['ip_novo_antecessor'] = self.node.ip
                string_json = json.dumps(msg)
                self.udp.sendto(string_json.encode('utf-8'), dest)
            elif string_dict["codigo"] == 65:
                print("Consegui sair")
            elif string_dict["codigo"] == 66:
                print(f"Resposta do Lookup: {string_dict['ip_sucessor']}")
                old = Node(string_dict['ip_origem'])

                dest = (string_dict["ip_sucessor"], self.node.porta)
                msg = {}
                msg["codigo"] = 0
                msg["id"] = string_dict["id_sucessor"]
                string_json = json.dumps(msg)
                self.udp.sendto(string_json.encode('utf-8'), dest)
            elif string_dict["codigo"] == 67:
                print("Conseguir entrar")

    def interface(self) -> None:
        while True:
            os.system("clear")
            print("######################################")
            print("# 1 - Criar uma nova rede P2P        #")
            print("# 2 - Entrar em uma rede P2P         #")
            print("# 3 - Sair da rede P2P               #")
            print("# 4 - Imprimir informa????es do n??     #")
            print("# 9 - Sair do programa               #")
            print("######################################")
            try:
                opc = int(input("=> "))
                if opc == 1:
                    if not self.node._inicializado:
                        self.node.sucessor = {"id": self.node.id, "ip": self.node.ip}
                        self.node.antecessor = {"id": self.node.id, "ip": self.node.ip}
                        self.node._inicializado = True
                        print("Rede P2P Inicializada!")
                    else:
                        print("Erro: rede P2P j?? foi inicializada!")
                    input("Pressione ENTER para continuar")
                elif opc == 2:
                    os.system("clear")
                    ip = input("Informe o IP do n??: ")
                    dest = (ip, self.node.porta)
                    msg = {}
                    msg["codigo"] = 2
                    msg["identificador"] = self.node.id
                    msg["ip_origem_busca"] = self.node.ip
                    msg["id_busca"] = self.node.id
                    string_json = json.dumps(msg)
                    self.udp.sendto(string_json.encode('utf-8'), dest)
                    print(f"Enviando msg para {ip}")
                    # enviar pacote UDP para o endere??o IP
                    input("Pressione ENTER para continuar")
                elif opc == 3:
                    os.system("clear")
                    msg = {}
                    dest = (self.node.sucessor["ip"], self.node.porta)
                    msg["codigo"] = 1
                    msg["identificador"] = self.node.id
                    msg["id_sucessor"] = self.node.sucessor["id"]
                    msg["ip_sucessor"] = self.node.sucessor["ip"]
                    msg["id_antecessor"] = self.node.antecessor["id"]
                    msg["ip_antecessor"] = self.node.antecessor["ip"]
                    self.udp.sendto(string_json.encode('utf-8'), dest)

                    msg = {}
                    dest = (self.node.antecessor["ip"], self.node.porta)
                    msg["codigo"] = 1
                    msg["identificador"] = self.node.id
                    msg["id_sucessor"] = self.node.sucessor["id"]
                    msg["ip_sucessor"] = self.node.sucessor["ip"]
                    msg["id_antecessor"] = self.node.antecessor["id"]
                    msg["ip_antecessor"] = self.node.antecessor["ip"]
                    self.udp.sendto(string_json.encode('utf-8'), dest)
                    
                elif opc == 4:
                    os.system("clear")
                    print("#      Informa????es do N??       #")
                    print(f"# ID: {self.node.id}")
                    print(f"# IP: {self.node.ip}")
                    print(f"# Sucessor: {self.node.sucessor}")
                    print(f"# Antecessor: {self.node.antecessor}")
                    print("#------------------------------#")
                    input("Pressione ENTER para continuar")
                elif opc == 9:
                    sys.exit(0)
            except ValueError:
                opc = 0


if __name__ == "__main__":
    if len(sys.argv) == 2:
        servidor = ServidorP2P(ip=sys.argv[1])
    else:
        print("Modo de utiliza????o: python3 main.py <ENDERE??O_IP>")
        sys.exit(0)
