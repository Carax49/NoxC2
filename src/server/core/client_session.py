# src/server/core/client_session.py

import time
from crypto import decrypt_with_config
from crypto import encrypt_with_config


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
        data = {
            'type': message_type,
            'uuid': self.__cid,
            'message_id': f'{self.__cid} - {self.__message_id}', # uuid - message id
            'timestamp' : int(time.time()),
            'data': data
        }
        message_json = self.__serializer.encode(data).decode("utf-8")
        encrypted_json = encrypt_with_config(message_json, self.__cid)
        self.__transport.send(self.__cid, encrypted_json.encode("utf-8"))
        self.__message_id += 1

    def receive_response(self):
        response = self.__transport.receive(self.__cid)
        if response is None:
            return None

        encrypted_json = response.decode("utf-8")
        message_json = decrypt_with_config(encrypted_json, self.__cid)
        decoded_response = self.__serializer.decode(message_json)
        return decoded_response
