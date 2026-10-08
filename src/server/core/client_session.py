# src/server/core/client_session.py

import json
import time
from config import MessageType as messtype


class ClientSession:

    def __init__(self):
        self.__cid = None
        self.__serializer = None
        self.__transport = None
        self.__message_id = 0

    def __str__(self):
        return (
            f"(cid = {self.__cid},\n"
            f"serializer = {self.__serializer},\n"
            f"transport = {self.__transport})\n"
            )

    def set_cid(self, cid):
        self.__cid = cid

    def set_serializer(self, serializer):
        self.__serializer = serializer

    def set_transport(self, transport):
        self.__transport = transport

    def send_request(self, message_type, data):
        # Tự động ghi nhận task vào CSDL SQLite khi gửi lệnh tới agent
        if message_type == messtype.COMMAND or message_type == "command":
            try:
                from db import TaskRepository, FileTransferRepository

                if isinstance(data, dict):
                    cmd_type = data.get("command", "dict_command")
                    clean_data = {k: v for k, v in data.items() if k != "file_data"}
                    payload_str = json.dumps(clean_data)
                    if cmd_type == "agent.upload":
                        FileTransferRepository.record_transfer(
                            agent_uuid=self.__cid,
                            direction="upload",
                            remote_path=data.get("file_path", ""),
                            local_path="",
                            file_size=data.get("file_size", 0),
                        )
                else:
                    payload_str = str(data)
                    parts = payload_str.split()
                    cmd_type = parts[0] if parts else "shell"

                TaskRepository.create_task(self.__cid, cmd_type, payload_str)
            except Exception:
                pass

        packet = {
            'type': message_type,
            'uuid': self.__cid,
            'message_id': f'{self.__cid} - {self.__message_id}', # uuid - message id
            'timestamp' : int(time.time()),
            'data': data
        }
        message_json = self.__serializer.encode(packet)
        self.__transport.send(self.__cid, message_json)
        self.__message_id += 1

    def receive_response(self):
        response = self.__transport.receive(self.__cid)
        if response is None:
            return None

        decoded_response = self.__serializer.decode(response)
        return decoded_response