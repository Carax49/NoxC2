# src/server/main.py

from core import Server
from transport import HTTPTransport
from serializer import JSONSerializer


if __name__ == "__main__":
    server = Server(HTTPTransport(), JSONSerializer())

    server.start()


