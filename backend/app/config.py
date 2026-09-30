"""
Application Configuration Module
--------------------------------
Provides type-safe, environment-variable-driven settings using Pydantic v2 BaseSettings.
Supports PostgreSQL production mode with seamless SQLite fallback for local developer workstations.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "Gujarat e-Vidya Scholarship Portal"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database: Default to SQLite for zero-config local testing, configurable to PostgreSQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR}/gujarat_evidya.db"
    )

    # Redis: Fallbacks automatically to thread-safe in-memory cache if redis server is unreachable
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_TIMEOUT_SECONDS: float = 1.0

    # JWT Authentication & Authorization (Q10: OWASP BOLA/IDOR Defense)
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "gujarat-evidya-secure-architectural-key-2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # AWS S3 Settings (Q12: AWS S3 Storage & Security)
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-south-1")
    AWS_S3_BUCKET_NAME: str = os.getenv("AWS_S3_BUCKET_NAME", "gujarat-evidya-income-certificates")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "MOCK_AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "MOCK_AWS_SECRET_ACCESS_KEY")
    S3_MOCK_MODE: bool = os.getenv("S3_MOCK_MODE", "true").lower() == "true"
    S3_PRESIGNED_EXPIRATION_SECONDS: int = 300  # Strict 5-minute expiry per Q12

    # UDISE+ / DigiLocker Central Gateway Settings (Q7: Central API Integration)
    UDISE_MOCK_BASE_URL: str = os.getenv("UDISE_MOCK_BASE_URL", "https://api.udiseplus.gov.in/mock")
    UDISE_CLIENT_ID: str = os.getenv("UDISE_CLIENT_ID", "gj_state_portal_client")
    UDISE_CLIENT_SECRET: str = os.getenv("UDISE_CLIENT_SECRET", "gj_secret_credential_token")
    UDISE_TIMEOUT_SECONDS: float = 2.0  # Strict 2-second timeout per Q7
    UDISE_CIRCUIT_FAILURE_THRESHOLD: int = 3
    UDISE_CIRCUIT_RECOVERY_TIMEOUT: float = 10.0

    # Rules Engine Configuration (Q6: Dynamic Rule-Based Automation)
    RULES_CONFIG_PATH: str = os.getenv(
        "RULES_CONFIG_PATH",
        str(BASE_DIR / "app" / "config" / "scholarship_rules.json")
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
