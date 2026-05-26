# src/server/crypto/aes_gcm.py

import base64
import json
import os
from typing import Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidTag

from config import SECRET_KEY


SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32
KDF_ITERS = 600_000
VERSION = 1
ALGORITHM = "AES-256-GCM"


def _derive_key(secret_key: str | bytes, salt: bytes) -> bytes:
    if isinstance(secret_key, str):
        secret_key = secret_key.encode("utf-8")

    if not isinstance(secret_key, (bytes, bytearray)):
        raise TypeError("secret_key must be str or bytes")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=KDF_ITERS,
    )
    return kdf.derive(bytes(secret_key))


def _validate_json_string(value: str, field_name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a JSON string")

    try:
        json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{field_name} must be valid JSON") from exc


def _build_aad(agent_id: str) -> bytes:
    if not isinstance(agent_id, str) or not agent_id:
        raise ValueError("agent_id must be a non-empty string")

    return json.dumps(
        {"agent_id": agent_id},
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _b64encode(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _b64decode(value: Any, field_name: str) -> bytes:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a base64 string")

    try:
        return base64.b64decode(value.encode("ascii"), validate=True)
    except (ValueError, UnicodeEncodeError) as exc:
        raise ValueError(f"{field_name} must be valid base64") from exc


def encrypt(secret_key: str | bytes, message_json: str, agent_id: str) -> str:
    """
    Encrypt a JSON string and return an encrypted JSON string.

    The crypto layer only accepts a JSON string that was already produced by the
    caller, for example: json.dumps(message_dict). It does not accept or return
    dictionaries.
    """
    _validate_json_string(message_json, "message_json")

    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    key = _derive_key(secret_key, salt)
    aad = _build_aad(agent_id)

    ciphertext = AESGCM(key).encrypt(
        nonce,
        message_json.encode("utf-8"),
        aad,
    )

    encrypted_message = {
        "version": VERSION,
        "alg": ALGORITHM,
        "salt": _b64encode(salt),
        "nonce": _b64encode(nonce),
        "ciphertext": _b64encode(ciphertext),
    }
    return json.dumps(encrypted_message, separators=(",", ":"))


def decrypt(secret_key: str | bytes, encrypted_json: str, agent_id: str) -> str:
    """
    Decrypt an encrypted JSON string and return the original JSON string.
    """
    _validate_json_string(encrypted_json, "encrypted_json")
    encrypted_message = json.loads(encrypted_json)

    if not isinstance(encrypted_message, dict):
        raise ValueError("encrypted_json must contain a JSON object")

    if encrypted_message.get("version") != VERSION:
        raise ValueError("unsupported encrypted message version")

    if encrypted_message.get("alg") != ALGORITHM:
        raise ValueError("unsupported encryption algorithm")

    salt = _b64decode(encrypted_message.get("salt"), "salt")
    nonce = _b64decode(encrypted_message.get("nonce"), "nonce")
    ciphertext = _b64decode(encrypted_message.get("ciphertext"), "ciphertext")

    if len(salt) != SALT_SIZE:
        raise ValueError("invalid salt size")

    if len(nonce) != NONCE_SIZE:
        raise ValueError("invalid nonce size")

    key = _derive_key(secret_key, salt)
    aad = _build_aad(agent_id)
    try:
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, aad)
    except InvalidTag as exc:
        raise ValueError("failed to decrypt message") from exc

    return plaintext.decode("utf-8")



def encrypt_with_config(message_json: str, agent_id: str) -> str:
    return encrypt(SECRET_KEY, message_json, agent_id)


def decrypt_with_config(encrypted_json: str, agent_id: str) -> str:
    return decrypt(SECRET_KEY, encrypted_json, agent_id)
