from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Project ARGUS Event Platform")
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")
    api_v1_prefix: str = Field(default="")
    database_url: str = Field(default="postgresql+asyncpg://argus:argus@localhost:5432/argus")
    kafka_bootstrap_servers: str = Field(default="localhost:9092")
    kafka_topic_events: str = Field(default="industrial.events")
    neo4j_uri: str = Field(default="bolt://localhost:7687")
    neo4j_username: str = Field(default="neo4j")
    neo4j_password: str = Field(default="argus-graph")
    neo4j_database: str = Field(default="neo4j")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
