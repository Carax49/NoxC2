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
    group = "host"

    def execute(self, *args):
        clist = Manager.get_client_list()

        if not clist:
            print("[blue_violet][!] No clients connected[/blue_violet]\n")
            return

        if len(args) == 0 or len(args) == 1 and args[0].lower() in ('-a', '--all'):
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
                print()


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
        print(f"[white]Total: {len(clist)} client(s)\n[/white]")

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
        table.add_row("SESSION", str(info.session))
        table.add_row("LAST BEACON", str(info.last_beacon))

        console = Console(width=MAX_TABLE_WIDTH)
        console.print(table)
        print()

    @staticmethod
    def get_help():
        help_detail = f"""
        Description : Show all / specific clients connected
        Usage : client.show [arguments]
        Arguments:
            {'<empty>/-a/--all':<20} : Show information of all clients
            {'<id>':<20} : Show information of specific client 
            {'<id1> <id2> ...':<20} : Show information of multiple clients

        Example : client.show all
                  client.show <id1> <id2> <id2> 
        """

        return help_detail