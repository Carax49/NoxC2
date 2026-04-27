import socket
import json


def recv_full(sock, n):
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data


if __name__ == '__main__':
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 4926))

    data = {
        'header': 'register',
        'data': {
            'uuid': '1234',
            'hostname': 'test-host',
            'username': 'carax',
            'os': 'Windows',
            'os_version': '11',
            'arch': 'x64'
        }
    }

    payload = json.dumps(data).encode()
    length = len(payload).to_bytes(4, byteorder='big')
    client.sendall(length + payload)

    while True:
        raw_len = recv_full(client, 4)
        if not raw_len:
            print("Server disconnected")
            break

        msg_len = int.from_bytes(raw_len, byteorder='big')

        payload = recv_full(client, msg_len)
        if not payload:
            print("Server disconnected")
            break

        msg = json.loads(payload.decode())
        print("Received:", msg)

        if msg.get('header') == 'command' and msg.get('data') == 'exit':
            print("Exit received")
            break

    client.close()