# src/server/transport/http_transport.py

import logging
import queue
import ssl
import threading

from flask import Flask, jsonify, request
from rich import print
from werkzeug.serving import make_server

import config as netcfg
from .base import BaseTransport

from typing import Callable, Optional

COMMAND_POLL_TIMEOUT = 50


class HTTPTransport(BaseTransport):

    def __init__(self, host=None, port=None, use_https=None):
        self.__host = host if host is not None else netcfg.HOST
        self.__port = port if port is not None else netcfg.HTTP_PORT
        self.__use_https = use_https if use_https is not None else netcfg.USE_HTTPS
        self.__app = Flask(__name__)
        self.__app.secret_key = netcfg.SECRET_KEY
        self.__on_client: Optional[Callable] = None
        self.__server = None
        self.__thread = None
        self.__send_queues = {}  # {uuid: queue} server -> client
        self.__recv_queues = {}  # {uuid: queue} client -> server
        self.__lock = threading.Lock()
        self.__register_routes()
        self.__register_api()

    def __str__(self):
        scheme = "https" if self.__use_https else "http"
        return f"HTTPTransport(scheme={scheme}, host={self.__host}, port={self.__port})"

    def __register_api(self):
        """Gắn REST API Blueprint (/api/*) và frontend (/) vào Flask app."""
        from .api import create_api_blueprint
        blueprint = create_api_blueprint()
        self.__app.register_blueprint(blueprint)

    def __register_routes(self):
        app = self.__app

        def _is_authorized():
            if netcfg.AGENT_KEY:
                token = request.headers.get('X-Agent-Key') or request.headers.get('Authorization')
                if token != netcfg.AGENT_KEY:
                    return False
            return True

        @app.route('/connect', methods=['POST'])
        def connect():
            if not _is_authorized():
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            uuid = request.headers.get('X-UUID')
            if not uuid:
                return jsonify({'status': 'error', 'message': 'Missing X-UUID header'}), 400

            addr = (request.remote_addr, request.environ.get('REMOTE_PORT', 0))
            self.__init_queues(uuid)
            self.__recv_queues[uuid].put(request.get_data())

            if self.__on_client:
                self.__on_client(uuid, addr)

            response_data = self.__wait_response(uuid, timeout=COMMAND_POLL_TIMEOUT)
            if response_data is None:
                return b'', 204

            return response_data, 200, {'Content-Type': 'application/octet-stream'}

        @app.route('/message', methods=['POST'])
        def message():
            if not _is_authorized():
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            uuid = request.headers.get('X-UUID')
            if not uuid:
                return jsonify({'status': 'error', 'message': 'Missing X-UUID header'}), 400

            if uuid not in self.__recv_queues:
                return jsonify({'status': 'error', 'message': 'Unknown client'}), 404

            addr = (request.remote_addr, request.environ.get('REMOTE_PORT', 0))
            self.__recv_queues[uuid].put(request.get_data())

            # Xử lý kết quả trong thread riêng để không block HTTP response.
            # Agent chỉ cần biết server đã nhận được — không cần chờ gì thêm.
            if self.__on_client:
                t = threading.Thread(target=self.__on_client, args=(uuid, addr), daemon=True)
                t.start()

            return b'', 204

        @app.route('/command', methods=['GET'])
        def command():
            if not _is_authorized():
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            uuid = request.headers.get('X-UUID')
            if not uuid:
                return jsonify({'status': 'error', 'message': 'Missing X-UUID header'}), 400

            if uuid not in self.__send_queues:
                return jsonify({'status': 'error', 'message': 'Unknown client'}), 404

            # Long-poll: chờ tối đa COMMAND_POLL_TIMEOUT giây cho lệnh mới.
            # Nếu hết giờ mà không có lệnh → 204, agent sẽ tự poll lại.
            response_data = self.__wait_response(uuid, timeout=COMMAND_POLL_TIMEOUT)
            if response_data is None:
                return b'', 204
            return response_data, 200, {'Content-Type': 'application/octet-stream'}

    def __init_queues(self, uuid):
        with self.__lock:
            if uuid not in self.__send_queues:
                self.__send_queues[uuid] = queue.Queue()
            if uuid not in self.__recv_queues:
                self.__recv_queues[uuid] = queue.Queue()

    def set_on_client(self, handler):
        self.__on_client = handler

    def start(self):
        logging.getLogger("werkzeug").disabled = True
        ssl_context = None

        if self.__use_https:
            if netcfg.ensure_ssl_certificates():
                try:
                    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                    ssl_context.load_cert_chain(
                        certfile=str(netcfg.SSL_CERT_PATH),
                        keyfile=str(netcfg.SSL_KEY_PATH)
                    )
                except Exception as e:
                    print(f"[yellow][!] Failed to load SSL certificates: {e}. Falling back to plain HTTP.[/yellow]")
                    ssl_context = None
            else:
                print("[yellow][!] OpenSSL is not available to generate self-signed certs. Falling back to plain HTTP.[/yellow]")

        if ssl_context:
            self.__server = make_server(self.__host, self.__port, self.__app, threaded=True, ssl_context=ssl_context)
            self.__thread = threading.Thread(target=self.__server.serve_forever, daemon=True)
            self.__thread.start()
            print(f"[bright_green][bright_magenta][HTTPS/TLS transport][/bright_magenta] "
                  f"listening on https://{self.__host}:{self.__port}[/bright_green]\n")
        else:
            self.__server = make_server(self.__host, self.__port, self.__app, threaded=True)
            self.__thread = threading.Thread(target=self.__server.serve_forever, daemon=True)
            self.__thread.start()
            print(f"[bright_green][bright_magenta][HTTP transport][/bright_magenta] "
                  f"listening on http://{self.__host}:{self.__port}[/bright_green]\n")

    def send(self, uuid, data):
        if uuid not in self.__send_queues:
            self.__init_queues(uuid)
        self.__send_queues[uuid].put(data)

    def receive(self, uuid):
        if uuid not in self.__recv_queues:
            self.__init_queues(uuid)
        return self.__recv_queues[uuid].get()

    def stop(self):
        if self.__server:
            self.__server.shutdown()
            self.__server = None

        if self.__thread:
            self.__thread.join(timeout=1)
            self.__thread = None

    def __wait_response(self, uuid, timeout=None):
        try:
            return self.__send_queues[uuid].get(timeout=timeout)
        except queue.Empty:
            return None