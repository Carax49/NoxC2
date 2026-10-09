# src/server/config/config.py

import os
import secrets
import shutil
import subprocess
from pathlib import Path


def _load_env():
    """
    Automatically load configuration from a .env file if present (no external library required).
    Searches current directory, project root, and server directory.
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


# Load environment variables from .env
_load_env()

# Project root path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# Database Configuration (SQLite)
DB_PATH = os.getenv("NOX_DB_PATH") or str(PROJECT_ROOT / "noxc2.db")

# Server Network Configuration
HOST = os.getenv("NOX_HOST", "127.0.0.1")
PORT = int(os.getenv("NOX_PORT", "4926"))
HTTP_PORT = int(os.getenv("NOX_HTTP_PORT", "8080"))
BUFFER_SIZE = int(os.getenv("NOX_BUFFER_SIZE", "4926"))  # bytes
TIMEOUT = int(os.getenv("NOX_TIMEOUT", "5"))  # seconds

MAX_WAITING_CLIENT = int(os.getenv("NOX_MAX_WAITING_CLIENT", "10"))
MAX_RETRIES = int(os.getenv("NOX_MAX_RETRIES", "5"))

# Server Security & Authentication Keys
# SECRET_KEY used for session / cookie / API token (randomly generated if not in .env)
SECRET_KEY = os.getenv("NOX_SECRET_KEY") or secrets.token_hex(32)

# AGENT_KEY: Pre-Shared Key (Agent authentication token on connection, empty = not required)
AGENT_KEY = os.getenv("NOX_AGENT_KEY", "")

# HTTPS / TLS Transport Configuration
USE_HTTPS = os.getenv("NOX_USE_HTTPS", "true").lower() in ("true", "1", "yes")

_DEFAULT_CERT_DIR = PROJECT_ROOT / "certs"
SSL_CERT_PATH = os.getenv("NOX_SSL_CERT") or str(_DEFAULT_CERT_DIR / "server.crt")
SSL_KEY_PATH = os.getenv("NOX_SSL_KEY") or str(_DEFAULT_CERT_DIR / "server.key")


def ensure_ssl_certificates() -> bool:
    """
    Ensure that the SSL certificate and private key exist.
    If not present, automatically generate a self-signed certificate using OpenSSL.
    Returns True on success, False on failure.
    """
    cert_path = Path(SSL_CERT_PATH)
    key_path = Path(SSL_KEY_PATH)

    if cert_path.is_file() and key_path.is_file():
        return True

    # Create destination directory if it does not exist
    cert_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if openssl is available in PATH
    openssl_bin = shutil.which("openssl")
    if not openssl_bin:
        # Check common Git / OpenSSL paths on Windows
        common_candidates = [
            r"C:\Program Files\Git\usr\bin\openssl.exe",
            r"C:\Program Files (x86)\Git\usr\bin\openssl.exe",
            r"C:\OpenSSL-Win64\bin\openssl.exe",
            r"C:\OpenSSL-Win32\bin\openssl.exe",
            r"C:\ProgramData\chocolatey\bin\openssl.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Git\usr\bin\openssl.exe"),
        ]
        for candidate in common_candidates:
            if os.path.isfile(candidate):
                openssl_bin = candidate
                break

    if not openssl_bin:
        return False

    try:
        cmd = [
            openssl_bin,
            "req",
            "-x509",
            "-newkey",
            "rsa:2048",
            "-keyout",
            str(key_path),
            "-out",
            str(cert_path),
            "-days",
            "365",
            "-nodes",
            "-subj",
            "/CN=127.0.0.1",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        return res.returncode == 0 and cert_path.is_file() and key_path.is_file()
    except Exception:
        return False



class MessageType:
    REGISTER = "register"
    ACK = "ack"
    COMMAND = "command"
    RESULT = "result"
