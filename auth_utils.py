"""Basic authentication utilities: password hashing + JWT-style tokens.

Pure standard-library implementation so there are no extra heavy deps.
Users are persisted in a local JSON file (users.json).
"""

import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import time

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "dev-secret-change-me-in-production")
TOKEN_TTL_SECONDS = 60 * 60 * 24  # 24 hours

PBKDF2_ITERATIONS = 100_000


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), PBKDF2_ITERATIONS
    ).hex()
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _algo, iterations, salt, digest = stored.split("$")
        check = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt), int(iterations)
        ).hex()
        return hmac.compare_digest(check, digest)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Tokens (compact HMAC-signed JWT, stdlib only)
# ---------------------------------------------------------------------------

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_token(username: str) -> str:
    header = _b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64url(
        json.dumps(
            {
                "sub": username,
                "iat": int(time.time()),
                "exp": int(time.time()) + TOKEN_TTL_SECONDS,
            }
        ).encode()
    )
    signature = _b64url(
        hmac.new(SECRET_KEY.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
    )
    return f"{header}.{payload}.{signature}"


def decode_token(token: str):
    """Return {'username': ...} or None if invalid/expired."""
    try:
        header, payload, signature = token.split(".")
        expected = _b64url(
            hmac.new(SECRET_KEY.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(expected, signature):
            return None
        data = json.loads(_b64url_decode(payload))
        if data.get("exp", 0) < time.time():
            return None
        return {"username": data["sub"]}
    except Exception:
        return None


# ---------------------------------------------------------------------------
# User store + validation
# ---------------------------------------------------------------------------

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.-]{3,32}$")


def _load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_users(users: dict):
    tmp = USERS_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(users, f, indent=2)
    os.replace(tmp, USERS_FILE)


def get_user(username: str):
    return _load_users().get(username)


def register_user(username: str, password: str):
    """Returns (success, message)."""
    username = username.strip()
    if not USERNAME_RE.match(username):
        return False, "Username must be 3-32 chars (letters, numbers, . _ -)"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    users = _load_users()
    key = username.lower()
    if key in users:
        return False, "Username already taken"
    users[key] = {"username": username, "password_hash": hash_password(password)}
    _save_users(users)
    return True, "Account created"


def authenticate_user(username: str, password: str):
    """Returns (success, token_or_message)."""
    user = _load_users().get(username.strip().lower())
    if not user or not verify_password(password, user["password_hash"]):
        return False, "Invalid username or password"
    return True, create_token(user["username"])
