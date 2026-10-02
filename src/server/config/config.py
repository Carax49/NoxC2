# src/server/config/config.py

import os
import secrets
from pathlib import Path


def _load_env():
    """
    Tự động đọc cấu hình từ file .env nếu có (không cần thư viện bên ngoài).
    Tìm kiếm ở thư mục hiện tại, thư mục root của project, hoặc thư mục server.
    """
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent.parent.parent / ".env",
        Path(__file__).resolve().parent.parent / ".env",
    ]
    for candidate in candidates:
        if candidate.is_file():
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k and k not in os.environ:
                                os.environ[k] = v
                break
            except Exception:
                pass


# Nạp biến môi trường từ .env
_load_env()

# Server Network Configuration
HOST = os.getenv("NOX_HOST", "127.0.0.1")
PORT = int(os.getenv("NOX_PORT", "4926"))
HTTP_PORT = int(os.getenv("NOX_HTTP_PORT", "8080"))
BUFFER_SIZE = int(os.getenv("NOX_BUFFER_SIZE", "4926"))  # bytes
TIMEOUT = int(os.getenv("NOX_TIMEOUT", "5"))  # seconds

MAX_WAITING_CLIENT = int(os.getenv("NOX_MAX_WAITING_CLIENT", "10"))
MAX_RETRIES = int(os.getenv("NOX_MAX_RETRIES", "5"))

# Server Security & Authentication Keys
# SECRET_KEY dùng cho session / cookie / API token (tự sinh ngẫu nhiên nếu không có trong .env)
SECRET_KEY = os.getenv("NOX_SECRET_KEY") or secrets.token_hex(32)

# AGENT_KEY: Pre-Shared Key (Token xác thực Agent lúc kết nối, rỗng = không yêu cầu)
AGENT_KEY = os.getenv("NOX_AGENT_KEY", "")

# SSL / TLS Settings (Dùng cho HTTPS Roadmap)
SSL_CERT_PATH = os.getenv("NOX_SSL_CERT", "")
SSL_KEY_PATH = os.getenv("NOX_SSL_KEY", "")


class MessageType:
    REGISTER = "register"
    ACK = "ack"
    COMMAND = "command"
    RESULT = "result"
