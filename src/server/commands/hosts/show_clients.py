# src/server/commands/hosts/show_clients.py

from commands import Command
from commands import register
from core import Manager
from rich import print
from rich.table import Table
from rich.console import Console

MAX_TABLE_WIDTH = 300

@register
class ShowClients(Command):
    name = "client.show"
    description = "Show all / specific clients connected"

    def execute(self, *args):
        clist = Manager.get_client_list()

        if not clist:
            print("[bright_blue][!] No clients connected[/bright_blue]")
            return

        if len(args) == 0:
            ShowClients.print_list(clist)
            return
        else:
            unknown_clients = []
            for cid in args:
                if cid in clist:
                    ShowClients.print_details(clist, cid)
                else:
                    unknown_clients.append(cid)
            if len(unknown_clients) > 0:
                print(f"[bright_red][!] Unknown clients: [/bright_red]")
                for cid in unknown_clients:
                    print(cid)


    @staticmethod
    def print_list(clist):
        table = Table(title="CLIENTS")

        table.add_column(header="SESSION ID", justify="center", no_wrap=True)
        table.add_column(header="HOSTNAME", justify="center", no_wrap=True)
        table.add_column(header="USERNAME", justify="center", no_wrap=True)
        table.add_column(header="IP", justify="center", no_wrap=True)
        table.add_column(header="PORT", justify="center", no_wrap=True)
        table.add_column(header="OS", justify="center", no_wrap=True)
        table.add_column(header="ARCHITECTURE", justify="center", no_wrap=True)
        table.add_column(header="LAST BEACON", justify="center", no_wrap=True)

        for cid, info in clist.items():
            table.add_row(
                f"{info.uuid}",
                f"{info.hostname}",
                f"{info.username}",
                f"{info.address[0]}",
                f"{info.address[1]}",
                f"{info.os}",
                f"{info.arch}",
                f"{info.last_beacon} (s)",
            )

        console = Console(width=MAX_TABLE_WIDTH)
        console.print(table)
        print(f"Total: {len(clist)} client(s)")

    @staticmethod
    def print_details(clist, uuid):
        info = clist[uuid]
        table = Table()
        table.add_column(header="FIELD", justify="center", no_wrap=True)
        table.add_column(header="DETAIL", justify="center", no_wrap=True)

        table.add_row("UUID", str(info.uuid))
        table.add_row("HOSTNAME", str(info.hostname))
        table.add_row("USERNAME", str(info.username))
        table.add_row("IP", str(info.address[0]))
        table.add_row("PORT", str(info.address[1]))
        table.add_row("OS", str(info.os))
        table.add_row("ARCH", str(info.arch))
        table.add_row("LAST BEACON", str(info.last_beacon))

        console = Console(width=MAX_TABLE_WIDTH)
        console.print(table)