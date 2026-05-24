# src/server/core/client_session.py

import time

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
        encode_data = self.__serializer.encode(data)
        self.__transport.send(self.__cid, encode_data)
        self.__message_id += 1

    def receive_response(self):
        response = self.__transport.receive(self.__cid)
        if response is None:
            return None

        decoded_response = self.__serializer.decode(response)
        return decoded_response
