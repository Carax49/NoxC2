# src/server/transport/tcp_transport.py

from .base import BaseTransport
from config import NetworkConfig as netcfg
from config import ClientConfig as clientcfg
import socket
from rich import print


class TCPTransport(BaseTransport):
    def __init__(self):
        self.__server = None

    def start(self):
        try:
            self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__server.bind((netcfg.HOST, netcfg.PORT))
            self.__server.listen(clientcfg.MAX_WAITING_CLIENT)
            self.__server.settimeout(netcfg.TIMEOUT)

            print(f"[bright_green][bright_magenta][TCP transport][/bright_magenta] "
                  f"listening on {netcfg.HOST}:{netcfg.PORT}[/bright_green]")

        except socket.error as e:
            print(f"[bright_red][ERROR][/bright_red] [bright_yellow]{e}[/bright_yellow]\n "
                  f"[bright_red]Cannot start server[/bright_red]")

            self.__server = None

    def accept(self):
        if self.__server is None:
            print("[bright_red][!] Can not connect to the server [/bright_red]")
            return None, None

        try:
            conn, addr = self.__server.accept()
            return conn, addr

        except socket.timeout as e:
            # print(f"[bright_red][!] Error: {e} [/bright_red]")
            return None, None
        except OSError:
            return None, None

    def stop(self):
        if self.__server:
            self.__server.close()
            self.__server = None

    def send(self, conn, data):
        length = len(data).to_bytes(4, byteorder='big')
        conn.sendall((length + data))

    def receive(self, conn):
        raw_length = TCPTransport.receive_all_data(conn, 4)
        if not raw_length:
            return None
        length = int.from_bytes(raw_length, byteorder='big')
        data = TCPTransport.receive_all_data(conn, length)
        if data is None:
            return data
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