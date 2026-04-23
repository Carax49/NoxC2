# src/server/main.py

from core import Server
from transport import TCPTransport
from serializer import JSONSerializer


if __name__ == "__main__":
    server = Server(TCPTransport(), JSONSerializer())

    server.start()


