# src/server/commands/interact/shell.py

from ..agent.agent_commands import Exit
from ..registry import GROUPS
from rich import print
import subprocess
import os

class Shell:
    def __init__(self):
        self.__current_client = set()  # uuid
        self.__running = True
        self.__exit_handler = None


    def promt(self):
        promt = '[NoxC2]> '

        if len(self.__current_client) > 0:
            promt = f'[{len(self.__current_client)} agent(s)]> '

        return promt

    def add(self, cid):
        self.__current_client.add(cid)

    def remove(self, cid):
        self.__current_client.discard(cid)

    def remove_all(self):
        self.__current_client.clear()

    def get_current_client(self):
        return self.__current_client

    def set_exit_handler(self, exit_handler):
        self.__exit_handler = exit_handler

    def run(self):
        try:
            while self.__running:
                current_promt = self.promt()
                print(f"[bright_cyan]{current_promt}[/bright_cyan]", end='')

                command = input().strip()
                if not command:
                    continue

                # -- sanitize --
                clean_command = ""

                for c in command:
                    if c.isprintable():
                        clean_command += c

                # -- built-in commands --
                if clean_command.lower() == 'exit':
                    result = self.__exit_handler()
                    if result == 0:
                        continue
                    else:
                        self.__running = False
                        Exit.execute(*self.__current_client)
                        break

                if clean_command.lower() == 'clear':
                    subprocess.run(['cls'] if os.name == 'nt' else ['clear'], shell=True)
                    continue

                # -- handle other commands --
                Shell.handle_command(clean_command)

        except KeyboardInterrupt as e:
            print(f"[bright_red][!] Shell interrupted {e}\n[*] Exiting shell[/bright_red]")


    @staticmethod
    def handle_command(command):

        handler = command.split()
        cmd = handler[0]
        args = handler[1:]

        if cmd in GROUPS['general']:
            GROUPS['general'][cmd].execute(*args)

        elif cmd in GROUPS['host']:
            GROUPS['host'][cmd].execute(*args)

        elif cmd in GROUPS['agent']:
            GROUPS['agent'][cmd].execute(*args)

        else:
            print(f"[!] Command [bright_red]'{cmd}'[/bright_red] not found")
            return

ShellManager = Shell()
