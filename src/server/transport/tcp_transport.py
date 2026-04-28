# src/server/transport/tcp_transport.py

from config import NetworkConfig as netcfg
from config import ClientConfig as clientcfg
from .base import BaseTransport
import socket
import time
import threading
from rich import print


class TCPTransport(BaseTransport):

    def __init__(self):
        self.__server = None
        self.__on_client = None
        self.__running = False

    def __str__(self):
        return f"TCPTransport(host={netcfg.HOST}, port={netcfg.PORT})"

    def set_on_client(self, on_client):
        self.__on_client = on_client


    def start(self):
        try:
            self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__server.bind((netcfg.HOST, netcfg.PORT))
            self.__server.listen(clientcfg.MAX_WAITING_CLIENT)
            self.__server.settimeout(netcfg.TIMEOUT)

            print(f"[bright_green][bright_magenta][TCP transport][/bright_magenta] "
                  f"listening on {netcfg.HOST}:{netcfg.PORT}[/bright_green]\n")
            time.sleep(0.7)

            self.__running = True
            accept_thread = threading.Thread(target=self.__accept_loop, daemon=True)
            accept_thread.start()

        except socket.error as e:
            print(f"[bright_red][ERROR][/bright_red] [bright_yellow]{e}[/bright_yellow]\n "
                  f"[bright_red]Cannot start server[/bright_red]")
            self.__server = None


    def __accept_loop(self):
        while self.__running:
            try:
                conn, addr = self.__server.accept()
                if self.__on_client:
                    print(f"[bright_green][+] New connection from {addr[0]}[/bright_green]")
                    client_thread = threading.Thread(
                        target=self.__on_client,
                        args=(conn, addr),
                        daemon=True
                    )
                    client_thread.start()

            except socket.timeout:
                continue
            except OSError:
                break


    def stop(self):
        self.__running = False
        if self.__server:
            self.__server.close()
            self.__server = None

    def send(self, conn, data):
        length = len(data).to_bytes(4, byteorder='big')
        conn.sendall(length + data)

    def receive(self, conn):
        raw_length = TCPTransport.receive_all_data(conn, 4)
        if not raw_length:
            return None
        length = int.from_bytes(raw_length, byteorder='big')
        data = TCPTransport.receive_all_data(conn, length)
        if data is None:
            return None
        return data.decode()

    @staticmethod
    def receive_all_data(conn, size_):
        buff = b''
        while len(buff) < size_:
            chunk = conn.recv(size_ - len(buff))
            if not chunk:
                return None
            buff += chunk
        return buff