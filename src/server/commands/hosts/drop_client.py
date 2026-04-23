# src/server/commands/hosts/drop_client.py

from commands.base import Command
from commands import register
from core import Manager
import time

@register
class DropClient(Command):
    name = "client.drop"
    description = "Remove specific / all client"

    def execute(self, *args):
        if 'all' in args:
            Manager.drop_all_clients()
            time.sleep(0.7)
            print("[+] Successfully removed all clients")
        else:
            try:
                invalid_clients = []
                valid_clients = []

                for cid in args:
                    if Manager.check_valid_cid(cid):
                        valid_clients.append(cid)
                        Manager.drop_client(cid)
                    else:
                        invalid_clients.append(cid)
                if len(valid_clients):
                    time.sleep(0.7)
                    print("[+] Successfully removed client(s)")
                if len(invalid_clients):
                    print(f"[bright_red][!] Unknown client(s):[/bright_red]\n {'\n'.join(invalid_clients)}")

            except OSError as e:
                print(f"[-] Error: {e}")