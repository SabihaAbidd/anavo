"""Explicit development origins; no wildcard or credentialed CORS."""
import os
from urllib.parse import urlsplit


def cors_origins():
    raw = os.getenv("ANAVO_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    origins = [value.strip() for value in raw.split(",") if value.strip()]
    for origin in origins:
        parts = urlsplit(origin)
        if (parts.scheme not in ("http", "https") or not parts.hostname or parts.username
            or parts.password or parts.path or parts.query or parts.fragment or "*" in origin):
            raise ValueError("ANAVO_CORS_ORIGINS must contain explicit HTTP(S) origins without paths or wildcards")
        try:
            parts.port
        except ValueError as exc:
            raise ValueError("CORS origin has an invalid port") from exc
    return list(dict.fromkeys(origins))
