# src/server/config/config.py

class NetworkConfig:
    HOST = "127.0.0.1"
    PORT = 4926
    BUFFER_SIZE = 4926  # byte
    TIMEOUT = 5 # second

class ClientConfig:
    MAX_WAITING_CLIENT = 10
    MAX_RETRIES = 5

class HeaderType:
    REGISTER = "register"
    ACK = "ack"
    COMMAND = "command"
    RESULT = "result"