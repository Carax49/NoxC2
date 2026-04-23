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

    handler_shell = Shell()

    def execute(self, *args):

        if len(args) == 1 and args[0] == "all":
            for cid in Manager.get_client_list():
                self.handler_shell.add(cid)

            print("[+] Successfully selected all clients")
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
            print(f"[+] Successfully selected client(s):\n{'\n'.join(valid_cid)}")

        if unknown_cid:
            print(f"[!] Unknown client(s):\n{'\n'.join(unknown_cid)}")