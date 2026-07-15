from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.uuid import generate_uuid
from app.reliability.models import AuditLog


class AuditService:
    async def append(
        self,
        session: AsyncSession,
        *,
        actor: str,
        action: str,
        reason: str,
        old_value: dict[str, Any],
        new_value: dict[str, Any],
        processor: str | None = None,
        rule: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            audit_id=generate_uuid(),
            actor=actor,
            action=action,
            reason=reason,
            old_value=old_value,
            new_value=new_value,
            processor=processor,
            rule=rule,
            context=context or {},
        )
        session.add(entry)
        await session.flush()
        return entry
