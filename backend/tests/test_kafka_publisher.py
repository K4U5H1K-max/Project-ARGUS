from __future__ import annotations

import pytest

from app.kafka.producer import AIOKafkaEventPublisher


@pytest.mark.asyncio
async def test_kafka_publisher_requires_startup() -> None:
    publisher = AIOKafkaEventPublisher(bootstrap_servers="localhost:9092", topic="industrial.events")

    with pytest.raises(RuntimeError):
        await publisher.publish({"hello": "world"})
