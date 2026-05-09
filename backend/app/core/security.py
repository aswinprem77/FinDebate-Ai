import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone

from app.core.config import settings


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000)
    return f"pbkdf2_sha256${salt}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, salt, encoded_digest = stored_hash.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False

    expected = base64.urlsafe_b64decode(encoded_digest.encode())
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000)
    return hmac.compare_digest(actual, expected)


def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expires_minutes)).timestamp()),
    }
    return _encode_jwt(payload)


def decode_access_token(token: str) -> str | None:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError:
        return None

    expected = _sign(f"{header_b64}.{payload_b64}".encode())
    if not hmac.compare_digest(signature_b64, expected):
        return None

    try:
        payload = json.loads(_b64decode(payload_b64))
    except (json.JSONDecodeError, ValueError):
        return None

    if payload.get("exp", 0) < int(datetime.now(timezone.utc).timestamp()):
        return None
    return payload.get("sub")


def _encode_jwt(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _b64encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = _b64encode(json.dumps(payload, separators=(",", ":")).encode())
    signature = _sign(f"{header_b64}.{payload_b64}".encode())
    return f"{header_b64}.{payload_b64}.{signature}"


def _sign(message: bytes) -> str:
    signature = hmac.new(settings.jwt_secret.encode(), message, hashlib.sha256).digest()
    return _b64encode(signature)


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode())
