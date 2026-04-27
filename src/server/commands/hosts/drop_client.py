# src/server/commands/hosts/drop_client.py

from commands.base import Command
from commands import register
from commands import ShellManager
from core import Manager
from rich import print
import time

@register
class DropClient(Command):
    name = "client.drop"
    description = "Drop specific / all client(s) from current session"
    group = "host"

    handler_shell = ShellManager

    def execute(self, *args):
        if not args:
            print(f"[blue_violet][!] No arguments provided. Use 'help {self.name}' for usage[/blue_violet]\n")
            return

        if len(self.handler_shell.get_current_client()) == 0:
            print("[blue_violet][!] No clients in use.[/blue_violet]\n")
            return

        if len(args) == 1 and args[0].lower() in ('-a', '--all'):
            self.handler_shell.remove_all()
            time.sleep(0.7)
            print("[blue_violet][+] Successfully dropped all clients[/blue_violet]\n")

        else:
            try:
                invalid_clients = []
                valid_clients = []

                for cid in args:
                    if cid in self.handler_shell.get_current_client():
                        valid_clients.append(cid)
                        self.handler_shell.remove(cid)
                    else:
                        invalid_clients.append(cid)

                if len(valid_clients):
                    time.sleep(0.7)
                    print(f"[blue_violet][+] Successfully dropped client(s):[/blue_violet]\n"
                          f"{'\n'.join(valid_clients)}")

                if len(invalid_clients):
                    print(f"[bright_red][!] Not in current selection:[/bright_red]\n {'\n'.join(invalid_clients)}")

            except OSError as e:
                print(f"[-] Error: {e}")

    @staticmethod
    def get_help():
        help_detail = f"""
        Description : Drop specific / all client(s) from current session
        Usage : client.drop [arguments]
        Arguments:
            {'-a/--all':<20} : Drop all clients
            {'<id>':<20} : Drop a specific client 
            {'<id1> <id2> ...':<20} : Drop multiple clients

        Example : client.drop --all
                  client.drop <id1> <id2> <id2>
                      
        """

        return help_detail