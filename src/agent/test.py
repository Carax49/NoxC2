import getpass
import json
import os
import platform
import socket
import time
import uuid
from socket import timeout as SocketTimeout
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SERVER_URL = "http://127.0.0.1:8080"
RECONNECT_DELAY = 3


AGENT_ID = str(uuid.uuid4())


def send_json(path, data):
    payload = json.dumps(data).encode("utf-8")
    request = Request(
        f"{SERVER_URL}{path}",
        data=payload,
        headers={
            "Content-Type": "application/octet-stream",
            "X-UUID": AGENT_ID,
        },
        method="POST",
    )

    with urlopen(request, timeout=30) as response:
        body = response.read()
        if not body:
            return None
        return json.loads(body.decode("utf-8"))


def get_command():
    request = Request(
        f"{SERVER_URL}/command",
        headers={"X-UUID": AGENT_ID},
        method="GET",
    )

    try:
        with urlopen(request, timeout=60) as response:
            body = response.read()
            if not body:
                return None
            return json.loads(body.decode("utf-8"))
    except TimeoutError:
        return None
    except SocketTimeout:
        return None


def collect_info():
    return {
        "uuid": AGENT_ID,
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "os": platform.system(),
        "os_version": platform.release(),
        "arch": platform.machine(),
    }


def run_demo_command(command):
    command = command.strip()

    if command == "agent.exit":
        return "agent.exit"
    if command == "whoami":
        return getpass.getuser()
    if command == "hostname":
        return socket.gethostname()
    if command == "pwd":
        return os.getcwd()
    if command == "platform":
        return platform.platform()
    if command.startswith("echo "):
        return command[5:]

    return f"Unsupported demo command: {command}"


def register():
    response = send_json(
        "/connect",
        {
            "type": "register",
            "uuid": AGENT_ID,
            "data": collect_info(),
        },
    )
    print(f"[+] Registered as {AGENT_ID}")
    print(f"[DEBUG] Server response: {response}")
    return response


def send_result(message_id, output):
    send_json(
        "/message",
        {
            "type": "result",
            "uuid": AGENT_ID,
            "message_id": message_id,
            "timestamp": int(time.time()),
            "data": output,
        },
    )


def handle_task(task):
    if task is None or task.get("type") != "command":
        return True

    command = task.get("data", "")
    message_id = task.get("message_id")
    print(f"[DEBUG] Received command: {command}")

    output = run_demo_command(command)
    if output == "agent.exit":
        send_result(message_id, "Agent exiting")
        print("[*] Exit command received")
        return False

    send_result(message_id, output)
    return True


def run_agent():
    while True:
        try:
            task = register()
            if not handle_task(task):
                return

            while True:
                if not handle_task(get_command()):
                    return

        except (HTTPError, URLError, TimeoutError, ConnectionError) as e:
            print(f"[!] Connection error: {e}")
        except KeyboardInterrupt:
            print("[*] Agent interrupted")
            return

        print(f"[*] Reconnecting in {RECONNECT_DELAY}s...\n")
        time.sleep(RECONNECT_DELAY)


if __name__ == "__main__":
    run_agent()
