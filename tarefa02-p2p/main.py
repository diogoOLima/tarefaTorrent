#!/usr/sbin/python3
# -*- coding: utf-8 -*-
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
                dest = (cliente, self.node.porta)
                msg = {}
                msg["codigo"] = 64
                msg["id_sucessor"] = self.node.id
                msg["ip_sucessor"] = self.node.ip
                msg["id_antecessor"] = self.node.antecessor["id"]
                msg["id_antecessor"] = self.node.antecessor["ip"]
                string_json = json.dumps(msg)
                self.udp.sendto(string_json.encode('utf-8'), dest)
            elif string_dict["codigo"] == 1:
                pass
            elif string_dict["codigo"] == 2:
                    if self.node.id == self.node.sucessor["id"]:
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
                    elif string_dict['id_busca'] > self.node.id and self.node.sucessor[id] < string_dict['id_busca']:
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
                    elif string_dict['id_busca'] < self.node.id:
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
                    elif string_dict['id_busca'] > self.node.id: 
                        dest = (self.node.sucessor, self.node.porta)
                        msg = {}
                        msg["codigo"] = 2
                        msg["identificador"] = string_dict['id_busca']
                        msg["ip_origem_busca"] = string_dict['ip_origem_busca']
                        msg["id_busca"] = string_dict['id_busca']
                        string_json = json.dumps(msg)
                        self.udp.sendto(string_json.encode('utf-8'), dest)


                    

            elif string_dict["codigo"] == 3:
                
                pass
            elif string_dict["codigo"] == 64:
                self.node.antecessor["id"] = string_dict["id_antecessor"]
                self.node.antecessor["ip"] = string_dict["ip_antecessor"]
                self.node.sucessor["id"] = string_dict["id_sucessor"]
                self.node.sucessor["ip"] = string_dict["ip_sucessor"]

                dest = (self.node.antecessor, self.node.porta)
                msg = {}
                msg['codigo'] = 3
                msg['identificador'] = self.node.id
                msg['id_novo_sucessor'] = self.node.id 
                msg['ip_novo_sucessor'] = self.node.ip
                string_json = json.dumps(msg)
                self.udp.sendto(string_json.encode('utf-8'), dest)

                dest = (self.node.sucessor, self.node.porta)
                msg = {}
                msg['codigo'] = 3
                msg['identificador'] = self.node.id
                msg['id_novo_antecessor'] = self.node.id 
                msg['ip_novo_antecessor'] = self.node.ip
                string_json = json.dumps(msg)
                self.udp.sendto(string_json.encode('utf-8'), dest)
            elif string_dict["codigo"] == 65:
                pass
            elif string_dict["codigo"] == 66:
                old = Node(string_dict['ip_origem'])

                dest = (string_dict["ip_sucessor"], self.node.porta)
                msg = {}
                msg["codigo"] = 0
                msg["id"] = string_dict["id_sucessor"]
                string_json = json.dumps(msg)
                self.udp.sendto(string_json.encode('utf-8'), dest)
            elif string_dict["codigo"] == 67:
                pass

    def interface(self) -> None:
        while True:
            os.system("clear")
            print("######################################")
            print("# 1 - Criar uma nova rede P2P        #")
            print("# 2 - Entrar em uma rede P2P         #")
            print("# 3 - Sair da rede P2P               #")
            print("# 4 - Imprimir informações do nó     #")
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
                        print("Erro: rede P2P já foi inicializada!")
                    input("Pressione ENTER para continuar")
                elif opc == 2:
                    os.system("clear")
                    ip = input("Informe o IP do nó: ")
                    dest = (ip, self.node.porta)
                    msg = {}
                    msg["codigo"] = 2
                    msg["identificador"] = self.node.id
                    msg["ip_origem_busca"] = self.node.ip
                    msg["id_busca"] = self.node.id
                    string_json = json.dumps(msg)
                    self.udp.sendto(string_json.encode('utf-8'), dest)
                    print(f"Enviando msg para {ip}")
                    # enviar pacote UDP para o endereço IP
                    input("Pressione ENTER para continuar")
                elif opc == 3:
                    pass
                elif opc == 4:
                    os.system("clear")
                    print("#      Informações do Nó       #")
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
        print("Modo de utilização: python3 main.py <ENDEREÇO_IP>")
        sys.exit(0)
