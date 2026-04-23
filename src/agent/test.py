import socket
import json


if __name__ == '__main__':
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 4926))

    data = {'header': 'register', 'data': {
        'uuid': '1234',
        'hostname': 'test-host',
        'username': 'carax',
        'os': 'Windows',
        'os_version': '11',
        'arch': 'x64'
    }}

    payload = json.dumps(data).encode()
    length = len(payload).to_bytes(4, byteorder='big')  # 4-byte length prefix
    client.sendall(length + payload)

    response = client.recv(4096)
    print(response.decode())

    client.close()