from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AuthContext:
    system: str
    subject: str


async def authenticate_stub() -> AuthContext:
    return AuthContext(system="stub", subject="anonymous")
