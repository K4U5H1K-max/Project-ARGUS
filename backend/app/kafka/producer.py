from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

from aiokafka import AIOKafkaProducer


class EventPublisher(ABC):
    is_ready: bool

    @abstractmethod
    async def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def stop(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def publish(self, event: dict[str, Any]) -> None:
        raise NotImplementedError


class AIOKafkaEventPublisher(EventPublisher):
    def __init__(self, *, bootstrap_servers: str, topic: str) -> None:
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self._producer: AIOKafkaProducer | None = None
        self.is_ready = False

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers, acks="all")
        await self._producer.start()
        self.is_ready = True

    async def stop(self) -> None:
        if self._producer is not None:
            await self._producer.stop()
        self.is_ready = False

    async def publish(self, event: dict[str, Any]) -> None:
        if self._producer is None:
            raise RuntimeError("Kafka producer is not started")
        payload = json.dumps(event, default=str).encode("utf-8")
        await self._producer.send_and_wait(self.topic, payload)
