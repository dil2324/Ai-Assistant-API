import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Final, cast, TypedDict

secret_key = os.getenv("JWT_SECRET_KEY")
if not secret_key:
    raise RuntimeError("JWT_SECRET_KEY not found")
SECRET_KEY: Final[str] = secret_key

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
SALT_BYTES = 16


class TokenPayload(TypedDict):
    sub: str
    type: str
    iat: int
    exp: int


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"pbkdf2_sha256$100000${_b64url_encode(salt)}${_b64url_encode(derived)}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password.startswith("pbkdf2_sha256$"):
        return False

    try:
        _, iterations_text, salt_b64, derived_b64 = hashed_password.split("$", 3)
        iterations = int(iterations_text)
        salt = _b64url_decode(salt_b64)
        expected_derived = _b64url_decode(derived_b64)
        derived = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iterations)
    except ValueError:
        return False

    return hmac.compare_digest(derived, expected_derived)


def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    
    payload: TokenPayload = {
        "sub": subject,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
    }

    header = {"alg": ALGORITHM, "typ": "JWT"}
    encoded_header = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    signature = hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{encoded_header}.{encoded_payload}.{_b64url_encode(signature)}"


def decode_access_token(token: str) -> TokenPayload | None:
    try:
        encoded_header, encoded_payload, signature = token.split(".")
    except ValueError:
        return None

    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    expected_signature = _b64url_encode(
        hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    )
    if not hmac.compare_digest(signature, expected_signature):
        return None

    try:
        header = json.loads(_b64url_decode(encoded_header).decode("utf-8"))
        raw = json.loads(_b64url_decode(encoded_payload).decode("utf-8"))
    except (ValueError, json.JSONDecodeError):
        return None

    if not isinstance(header, dict) or header.get("alg") != ALGORITHM:
        return None
    if not isinstance(raw, dict):
        return None
    if not isinstance(raw.get("sub"), str):
        return None
    if not isinstance(raw.get("type"), str):
        return None
    if not isinstance(raw.get("iat"), int):
        return None
    if not isinstance(raw.get("exp"), int):
        return None

    payload = cast(TokenPayload, raw)

    if payload["type"] != "access":
        return None

    # Check token expiration.
    exp = payload["exp"]
    if exp < int(datetime.now(timezone.utc).timestamp()):
        return None

    return payload
