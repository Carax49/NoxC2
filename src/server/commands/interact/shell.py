# src/server/commands/interact/shell.py

import os
from rich import print
import subprocess
from commands import GROUPS

class Shell:
    def __init__(self):
        self.__current_client = set()  # uuid
        self.__running = True


    def promt(self):
        promt = '[NoxC2]> '

        if len(self.__current_client) > 0:
            promt = f'[{len(self.__current_client)} agent(s)]>'

        return promt

    def add(self, cid):
        self.__current_client.add(cid)

    def remove(self, cid):
        self.__current_client.discard(cid)

    def remove_all(self):
        self.__current_client.clear()

    def get_current_client(self):
        return self.__current_client

    def run(self):
        try:
            while self.__running:
                    print(f"[bright_cyan]{self.promt()}[/bright_cyan]", end='')

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
                        check = self.exit()
                        if check:
                            self.__running = False
                            break
                        continue

                    if clean_command.lower() == 'clear':
                        subprocess.run(['cls'] if os.name == 'nt' else ['clear'])
                        continue

                    # -- handle other commands --
                    Shell.handle_command(clean_command)

        except KeyboardInterrupt as e:
            print(f"[bright_red][!] Shell interrupted {e}\n[*] Exiting shell[/bright_red]")


    @staticmethod
    def exit():
        while True:
            print("[bright_red][!] Exit ? (y/n): [/bright_red]", end="")
            confirm = input().strip()

            if confirm.lower() == 'y':

                return 1
            elif confirm.lower() == 'n':
                return 0
            else:
                continue


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