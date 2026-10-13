#!/usr/bin/env python3

import socket    # Para hacer las conexiones de red a los puertos
import argparse  # Para leer comandos de la terminal (ej: -t 192.168.1.1)
import sys       # Para poder cerrar el programa de golpe si hay un error
import concurrent.futures
import threading #para tener mutex/semaforos 
import time # para usar la funcion time y ver cuánto tarda

#variables globales, fuera de las funciones 
contador_puertos = 0
mutex = threading.Lock()

def iniciar_parser():
    
    parser = argparse.ArgumentParser(description="Port Scaner script")
    # 1. EL ARGUMENTO POSICIONAL (Sin guiones). 
    # Será obligatorio y recogerá lo primero que escribas después del script.
    parser.add_argument("ip", help="Ip a escanear")
    parser.add_argument("-ap", "--all_port",action="store_true", help="Puertos a escanear en formato rango")
    parser.add_argument("-tp", "--top_ports",action="store_true", help="Escanea los puertos más populares")
    parser.add_argument("-t", "--time", type=float, default=0.5, help="Tiempo maximo de espera") 
    argumentos = parser.parse_args()
    return argumentos.ip, argumentos.all_port, argumentos.top_ports, argumentos.time

def conexion_socket(ip_dst, puerto, time):
    conexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tupla_ip_puerto = (ip_dst, puerto)
    conexion.settimeout(time) #Tiempo max de espera (se tieen que definir antes de conectarse)
    res = conexion.connect_ex(tupla_ip_puerto)
    #connect.ex a diferencia de connect, cuando no se conecta 
    #simplemente devuelve 1 en vez de crash

    #indicamos que vamos a usar la variable global
    global contador_puertos
    
    if res == 0:
        with mutex:
            print(f"[+] Puerto {puerto} ABIERTO")
            contador_puertos+=1
    conexion.close()


if __name__ == "__main__":
    argumentos = iniciar_parser()
    ip_target = argumentos[0]
    if argumentos[1]: #all_port = True
        puertos = list(range(1, 65536))
    elif argumentos[2]: #top_ports
        puertos = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 1433, 3306, 3389, 8080]
    else:
        puertos = list(range(1,1025))
    tiempo_espera = argumentos[3]
    inicio = time.time()
    print("=======Iniciando escaneo=======")
    with concurrent.futures.ThreadPoolExecutor(max_workers=150) as executor:
        for port in puertos:
            executor.submit(conexion_socket, ip_target, port, tiempo_espera)
    if contador_puertos == 0:
        print(f"No hay puertos abiertos en esta maquina")
    print("\n")
    final = time.time()
    tiempo_total = final - inicio
    print(f"Tiempo total: {tiempo_total}")
    print("=========Fin del escaneo=========")






