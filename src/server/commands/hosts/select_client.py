# src/server/commands/hosts/select_client.py

from ..base import Command
from ..interact.shell import ShellManager
from ..registry import register
from core.client_manager import Manager
from rich import print

@register
class SelectClient(Command):
    name = "client.select"
    description = "Select client to interact with"
    group = "host"

    handler_shell = ShellManager

    def execute(self, *args):
        if not args:
            print(f"[blue_violet][!] No arguments provided. Use 'help {self.name}' for usage[/blue_violet]\n")
            return

        if len(args) == 1 and args[0].lower() in ('-a', '--all'):
            if len(Manager.get_client_list()):
                for cid in Manager.get_client_list():
                    self.handler_shell.add(cid)

                print("[blue_violet][+] Successfully selected all clients[/blue_violet]\n")
            else:
                print(f"[blue_violet][!] Clients list is empty[/blue_violet]\n")

            return

        if len(args) == 1 and args[0].lower() in ("--list", "-ls"):
            if len(self.handler_shell.get_current_client()):
                for cid in self.handler_shell.get_current_client():
                    print(cid)
            else:
                print(f"[blue_violet][!] Current clients list is empty[/blue_violet]\n")

            return
        valid_cid = []
        unknown_cid = []

        for cid in args:
            if cid != '--add':
                if Manager.check_valid_cid(cid):
                    valid_cid.append(cid)
                else:
                    unknown_cid.append(cid)

        if valid_cid:
            if '--add' not in args:
                self.handler_shell.remove_all()

                for cid in valid_cid:
                    self.handler_shell.add(cid)

            print(f"[blue_violet][+] Successfully selected client(s):[/blue_violet]\n{'\n'.join(valid_cid)}\n")

        if unknown_cid:
            print(f"[bright_red][!] Unknown client(s):\n{'\n'.join(unknown_cid)}[/bright_red]\n")


    @staticmethod
    def get_help():
        help_detail = f"""
        Description : Select client to interact with
        Usage : client.select [arguments]
        Arguments:
            {'-a/--all':<20} : Select all clients
            {'-ls/--list':<20} : List all selected clients
            {'--add':<20} : Add to current selection instead of replacing
            {'<id>':<20} : Select specific client to interact with
            {'<id1> <id2> ...':<20} : Select specific clients to interact with
            
            Note : By default, selecting new clients will CLEAR the current selection.
                   Use '--add' to keep the current selection.
            
        Example : client.select <id1> <id2> <id3>
                  client.select --add <id1> <id2> 
                  client.select --list 
        """

        return help_detail
