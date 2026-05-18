# src/server/config/config.py

class NetworkConfig:
    HOST = "127.0.0.1"
    PORT = 4926
    HTTP_PORT = 8080
    BUFFER_SIZE = 4926  # byte
    TIMEOUT = 5 # second

class ClientConfig:
    MAX_WAITING_CLIENT = 10
    MAX_RETRIES = 5

class MessageType:
    # Message Types
    # {
    #     'type'        : message Type,     (register/result/request)
    #     'uuid'        : agent_uuid,       (uuidv4)
    #     'id'          : message_id,       (uuid - id)
    #     'timestamp'   : timestamp,
    #     'data'        : {}
    # }

    REGISTER = "register"
    ACK = "ack"
    COMMAND = "command"
    RESULT = "result"