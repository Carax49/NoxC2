# src/server/commands/interact/shell.py

from commands import REGCOMMANDS

class Shell:
    def __init__(self):
        self.__current_client = set()  # uuid
        self.__running = True


    def promt(self):
        promt = '[shell]> '

        if len(self.__current_client) > 0:
            promt = f'[{len(self.__current_client)} client(s)]>'

        return promt

    def add(self, cid):
        self.__current_client.add(cid)

    def remove(self, cid):
        self.__current_client.remove(cid)

    def run(self):
        while self.__running:
            try:
                command = input(self.promt()).strip()
                if not command:
                    continue

                clean_command = ""

                for c in command:
                    if c.isprintable():
                        clean_command += c

                if clean_command.lower() == 'exit':
                    self.__running = False
                    print("[*] Exiting shell")
                    break

                Shell.handle_command(clean_command)

            except KeyboardInterrupt as e:
                print(f"[bright_red][!] Shell interrupted {e}\n[*] Exiting shell[/bright_red]")


    @staticmethod
    def handle_command(command):

        handler = command.split()
        cmd = handler[0]
        args = handler[1:]

        if cmd not in REGCOMMANDS:
            print(f"[!] Command '{cmd}' not found")
            return

        REGCOMMANDS[cmd].execute(*args)