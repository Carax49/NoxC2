# src/server/commands/hosts/remove_client.py

from commands.base import Command
from commands import register
from commands import ShellManager
from commands import Exit
from core import Manager
from rich import print
import time


@register
class RemoveClient(Command):
    name = "client.remove"
    description = "Remove specific / all client(s) from the server"
    group = "host"

    handler_shell = ShellManager

    def execute(self, *args):
        if not args:
            print(f"[blue_violet][!] No arguments provided. Use 'help {self.name}' for usage[/blue_violet]\n")
            return

        if len(Manager.get_client_list()) == 0:
            print("[blue_violet][!] No clients connected to the server[/blue_violet]\n")
            return

        if len(args) == 1 and args[0].lower() in ('-a', '--all'):
            for cid in Manager.get_client_list():
                Exit.execute(cid)

            Manager.drop_all_clients()
            self.handler_shell.remove_all()
            time.sleep(0.7)
            print("[blue_violet][+] Successfully removed all clients[/blue_violet]\n")

        else:
            try:
                invalid_clients = []
                valid_clients = []

                for cid in args:
                    if Manager.check_valid_cid(cid):
                        valid_clients.append(cid)
                        Exit.execute(cid)

                        Manager.drop_client(cid)
                        self.handler_shell.remove(cid)
                    else:
                        invalid_clients.append(cid)

                if len(valid_clients):
                    time.sleep(0.7)
                    print(f"[blue_violet][+] Successfully removed client(s):[/blue_violet]\n"
                          f"{'\n'.join(invalid_clients)}")

                if len(invalid_clients):
                    print(f"[bright_red][!] Unknown client(s):[/bright_red]\n {'\n'.join(invalid_clients)}")

            except OSError as e:
                print(f"[-] Error: {e}")

    @staticmethod
    def get_help():
        help_detail = f"""
        Description : Disconnect specific / all client(s) from the server 
        Usage : client.remove [arguments]
        Arguments:
            {'-a/--all':<20} : Remove all clients
            {'<id>':<20} : Remove a specific client 
            {'<id1> <id2> ...':<20} : Remove multiple clients

        Example : client.remove all
                  client.remove <id1> <id2> <id2>

        """

        return help_detail