#!/usr/bin/env python

from scapy.all import IP, TCP, sr1, send
import argparse
import concurrent.futures
import time
import threading

contador_puertos = 0
mutex = threading.Lock()


def escaneo(ip_target, port):
    global contador_puertos
    #IP / TCP -> IP encapsula TCP (TCP esta como payload de IP)
    paquete = IP(dst=ip_target) / TCP(dport=port, flags="S")
    #sr1 = send recive 1, envia paquete y espera una respuesta (guarda la 1ra resp.)
    respuesta = sr1(paquete, timeout=0.4, verbose=0)
    if respuesta is not None:
        #print("Respuesta recibida")
        if respuesta.haslayer(TCP): #si la respuesta tiene capa TCP
            flags = respuesta[TCP].flags
            #print(f"Banderas recibidas: {flags}")
            if flags == "SA": #syn-ack
                #creo un paquete de RST para cerrar la conexion antes de establecerla
                paqueteRST = IP(dst=ip_target) / TCP(dport = port, flags="R")
                send(paqueteRST, verbose=0)
                print(f"[+] Puerto {port} abierto")
                with mutex:
                    contador_puertos+=1
                
            #elif flags == "R" or flags == "RA":
                #print(f"Puerto {port} cerrado")

    #else:
        #print("Sin respuesta")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stealth scanner")
    
    parser.add_argument("ip", help="Ip de la victima")
    parser.add_argument("-tp", "--top_ports", action="store_true", help="Escaneo de los puertos comunes")
    argumentos = parser.parse_args()
    ip = argumentos.ip 
    if argumentos.top_ports:
        puertos = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 1433, 3306, 3389, 8080]
    else:
        puertos = list(range(1, 65536))
    inicio = time.time()
    print("\n========Iniciando Escaneo Sigiloso========\n")
    print("UTILIZAR SUDO")
    #scapy cada vez que envia un paquete abre un sniffer y muchos hilos lo colapsa
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for port in puertos:
            executor.submit(escaneo, ip, port)
    if contador_puertos == 0:
        print("No hay puertos abiertos\n")
    final = time.time()
    print(f"Tiempo total = {final-inicio} segundos \n")
    print("========Final Stealth Scan========")





