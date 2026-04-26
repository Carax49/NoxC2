# src/server/commands/hosts/drop_client.py

from commands.base import Command
from commands import register
from commands import Shell
from core import Manager
from rich import print
import time

@register
class DropClient(Command):
    name = "client.drop"
    description = "Disconnect specific / all client(s) from the server"
    group = "host"

    handler_shell = Shell()

    def execute(self, *args):
        if len(Manager.get_client_list()) == 0:
            print("[blue_violet][!] No clients connected to the server[/blue_violet]\n")
            return

        if len(args) == 1 and args[0].lower() == "all":
            Manager.drop_all_clients()
            self.handler_shell.remove_all()
            time.sleep(0.7)
            print("[blue_violet][+] Successfully dropped all clients[/blue_violet]\n")

        else:
            try:
                invalid_clients = []
                valid_clients = []

                for cid in args:
                    if Manager.check_valid_cid(cid):
                        valid_clients.append(cid)
                        Manager.drop_client(cid)
                        self.handler_shell.remove(cid)
                    else:
                        invalid_clients.append(cid)

                if len(valid_clients):
                    time.sleep(0.7)
                    print(f"[blue_violet][+] Successfully dropped client(s):[/blue_violet]\n"
                          f"{'\n'.join(invalid_clients)}")

                if len(invalid_clients):
                    print(f"[bright_red][!] Unknown client(s):[/bright_red]\n {'\n'.join(invalid_clients)}")

            except OSError as e:
                print(f"[-] Error: {e}")

    @staticmethod
    def get_help():
        help_detail = f"""
        Description : Disconnect specific / all client(s) from the server 
        Usage : client.drop [arguments]
        Arguments:
            {'all':<20} : Drop all clients
            {'<id>':<20} : Drop a specific client 
            {'<id1> <id2> ...':<20} : Drop multiple clients

        Example : client.drop all
                  client.drop <id1> <id2> <id2>
                      
        """

        return help_detail