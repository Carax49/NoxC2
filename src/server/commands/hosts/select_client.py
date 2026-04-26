# src/server/commands/hosts/select_client.py

from commands.base import Command
from commands import register
from commands import Shell
from core import Manager
from rich import print

@register
class SelectClient(Command):
    name = "client.select"
    description = "Select client to interact with"
    group = "host"

    handler_shell = Shell()

    def execute(self, *args):

        if len(args) == 1 and args[0].lower() == "all":
            if len(Manager.get_client_list()):
                for cid in Manager.get_client_list():
                    self.handler_shell.add(cid)

                print("[blue_violet][+] Successfully selected all clients[/blue_violet]\n")
            else:
                print(f"[blue_violet][!] Clients list is empty[/blue_violet]\n")

            return

        if len(args) == 1 and args[0].lower() in ("list", "ls"):
            if len(self.handler_shell.get_current_client()):
                for cid in self.handler_shell.get_current_client():
                    print(cid)
            else:
                print(f"[blue_violet][!] Current clients list is empty[/blue_violet]\n")

            return

        valid_cid = []
        unknown_cid = []

        for cid in args:
            if Manager.check_valid_cid(cid):
                valid_cid.append(cid)
                self.handler_shell.add(cid)
            else:
                unknown_cid.append(cid)

        if valid_cid:
            print(f"[blue_violet][+] Successfully selected client(s):[/blue_violet]\n{'\n'.join(valid_cid)}\n")

        if unknown_cid:
            print(f"[bright_red][!] Unknown client(s):\n{'\n'.join(unknown_cid)}[/bright_red]\n")

    @staticmethod
    def get_help():
        help_detail = f"""
        Description : Select client to interact with
        Usage : client.select [arguments]
        Arguments:
            {'all':<20} : Select all clients
            {'ls/list':<20} : List all selected clients
            {'<id>':<20} : Select specific client to interact with
            {'<id1> <id2> ...':<20} : Select specific clients to interact with
            
        Example : client.select <id1> <id2> <id2>
                  client.select ls 
        """

        return help_detail