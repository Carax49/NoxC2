# src/server/core/client_session.py


class ClientSession:

    def __init__(self):
        self.__cid = None
        self.__client = None
        self.__serializer = None
        self.__transport = None

    def __str__(self):
        return (
            f"(cid = {self.__cid},\n"
            f"serializer = {self.__serializer},\n"
            f"transport = {self.__transport})\n"
            )

    def set_cid(self, cid):
        self.__cid = cid

    def set_client(self, client):
        self.__client = client

    def set_serializer(self, serializer):
        self.__serializer = serializer

    def set_transport(self, transport):
        self.__transport = transport

    def send_request(self, header, data):
        data = {
            'header': header,
            'data': data
        }
        encode_data = self.__serializer.encode(data)
        self.__transport.send(self.__client, encode_data)

    def receive_respone(self):
        respone = self.__transport.receive(self.__client)
        if respone is None:
            return None

        decode_respone = self.__serializer.decode(respone)
        return decode_respone