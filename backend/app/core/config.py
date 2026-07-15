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
    risk_critical_threshold: int = Field(default=85, ge=1, le=100)
    risk_high_threshold: int = Field(default=65, ge=1, le=100)
    risk_moderate_threshold: int = Field(default=40, ge=1, le=100)
    risk_history_limit: int = Field(default=25, ge=1, le=500)
    risk_temporal_window_minutes: int = Field(default=30, ge=1, le=1440)
    risk_hazard_radius_meters: int = Field(default=30, ge=1, le=1000)
    risk_density_threshold: int = Field(default=5, ge=1, le=100)
    risk_score_rule_weight: float = Field(default=0.55, ge=0.0, le=2.0)
    risk_score_confidence_weight: float = Field(default=22.0, ge=0.0, le=50.0)
    risk_score_exposure_weight: float = Field(default=10.0, ge=0.0, le=50.0)
    risk_score_spatial_weight: float = Field(default=8.0, ge=0.0, le=50.0)
    risk_score_temporal_weight: float = Field(default=12.0, ge=0.0, le=50.0)
    risk_score_compound_weight: float = Field(default=6.0, ge=0.0, le=50.0)
    risk_score_history_weight: float = Field(default=8.0, ge=0.0, le=50.0)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
