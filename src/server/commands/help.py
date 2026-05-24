# src/server/commands/help.py

from .base import Command
from .registry import AGENT_COMMANDS
from .registry import GENERAL_COMMANDS
from .registry import HOST_COMMANDS
from .registry import register
from rich.markup import escape
from rich import print

@register
class Help(Command):
    name = 'help'
    description = 'Show help menu'
    group = 'general'

    def execute(self, *args):
        if len(args) == 0:
            print(f"[bold white]{'--- HELP MENU ---':>30}[/bold white]\n")
            print(f"[white]Tip: help <command> for detailed usage[/white]")

            print("[bold bright_magenta]\nGENERAL COMMANDS[/bold bright_magenta]")
            print("[white]----------[/white]")

            for cmd, cmd_cls in GENERAL_COMMANDS.items():
                print(f"[white]{cmd:<20}: {cmd_cls.description}[/white]")

            print(f"[white]{'clear':<20}: Clear the screen[/white]")
            print(f"[white]{'exit':<20}: Exit the shell[/white]")

            print("[bold bright_magenta]\nHOST COMMANDS[/bold bright_magenta]")
            print("[white]----------[/white]")

            for cmd, cmd_cls in HOST_COMMANDS.items():
                print(f"[white]{cmd:<20}: {cmd_cls.description}[/white]")

            print("[bold bright_magenta]\nAGENT COMMANDS[/bold bright_magenta]")
            print("[white]----------[/white]")

            for cmd, cmd_cls in AGENT_COMMANDS.items():
                print(f"[white]{cmd:<20}: {cmd_cls.description}[/white]")

            print()
        else:
            for cmd in args:
                Help.detail(cmd)

    @staticmethod
    def detail(command):
        if command == 'clear':
            print(f"[white][bright_magenta]{'clear':<10}[/bright_magenta]: Clear the screen[/white]\n")
            return

        if command == 'exit':
            print(f"[white][bright_magenta]{'exit':<10}[/bright_magenta]: Exit the shell[/white]\n")
            return

        if command in GENERAL_COMMANDS:
            print(f"\n[white][bright_magenta]{command}[/bright_magenta]\n"
                  f"----------"
                  f"{escape(GENERAL_COMMANDS[command].get_help())}[/white]")

        elif command in HOST_COMMANDS:
            print(f"\n[white][bright_magenta]{command}[/bright_magenta]\n"
                  f"----------"
                  f"{escape(HOST_COMMANDS[command].get_help())}[/white]")

        elif command in AGENT_COMMANDS:
            print(f"\n[white][bright_magenta]{command}[/bright_magenta]\n"
                  f"----------"
                  f"{escape(AGENT_COMMANDS[command].get_help())}[/white]")

        else:
            print(f"[!] Command [bright_red]'{command}'[/bright_red] not found\n")

    @staticmethod
    def get_help():
        help_detail = f"""
        Description : Show help menu
        Usage : help [arguments]
        Arguments:
            {'<empty>':<20} : Show help menu
            {'<command>':<20} : Get help for a specific command
            {'<cmd_1> <cmd_2> ...':<20} : Get help for multiple commands
            
        Examples : help client.show
                """

        return help_detail
