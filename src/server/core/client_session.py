# src/server/core/client_session.py


class ClientSession:

    def __init__(self):
        self.__client = None
        self.__serializer = None
        self.__transport = None

    def set_client(self, client):
        self.__client = client

    def set_serializer(self, serializer):
        self.__serializer = serializer

    def set_transport(self, transport):
        self.__transport = transport

    def send_request(self, header, data):
        data = {
            'header': header,
            'command': data
        }
        encode_data = self.__serializer.encode(data)
        self.__transport.send(self.__client, encode_data)

    def receive_respone(self):
        respone = self.__transport.receive(self.__client)
        if respone is None:
            return None

        decode_respone = self.__serializer.decode(respone)
        return decode_respone