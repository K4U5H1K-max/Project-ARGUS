from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request


@dataclass(frozen=True, slots=True)
class AuthContext:
    system: str
    subject: str


async def authenticate_request(request: Request) -> AuthContext:
    subject = request.headers.get("X-Client-Id", "anonymous")
    return AuthContext(system="header", subject=subject)
