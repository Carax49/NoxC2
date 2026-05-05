# src/server/transport/http_transport.py

from .base import BaseTransport
from config import NetworkConfig as netcfg
# from flask import Flask
from rich import print
import threading
import queue
import time


# class HTTPConn:
#     def __init__(self, agent_id, address):
#         self.agent_id = agent_id
#         self.address = address
#         self.send_queue = queue.Queue()
#         self.receive_queue = queue.Queue()


class HTTPTransport(BaseTransport):

    pass

    # def __init__(self):
    #     self.app = Flask(__name__)
    #     self.on_client = None
    #     self.lock = threading.Lock()
    #
    # def set_on_client(self, on_client):
    #     self.on_client = on_client
    #
    # def run_flask(self):
    #     self.app.run(host = netcfg.HOST, port = netcfg.HTTP_PORT, threaded = True)
    #
    # def start(self):
    #     try:
    #         http_thread = threading.Thread(target=self.run_flask, daemon=True)
    #         http_thread.start()
    #
    #         print(f"[bright_green][bright_magenta][HTTP transport][/bright_magenta] "
    #               f"listening on {netcfg.HOST}:{netcfg.HTTP_PORT}[/bright_green]\n")
    #         time.sleep(0.7)
    #
    #     except Exception as e:
    #         print(f"[bright_red][ERROR][/bright_red] [bright_yellow]{e}[/bright_yellow]\n "
    #               f"[bright_red]Cannot start server[/bright_red]")
    #
    # # ------------- Base Transport -------------
    #
    # def send(self, conn, data):
    #     conn.send_queue.put(data)
    #
    # def receive(self, conn, data):
    #     conn.receive_queue.put(data)
    #
    # def stop(self):
    #     pass
    #
    # # ------------------------------------------