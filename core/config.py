"""
Konfigurimi global i aplikacionit AutoServis API.

Vlerat lexohen me prioritetin (më të lartë → më të ulët):
    1. Variabla mjedisi (export DATABASE_URL=...)
    2. File-i .env në rrënjë të projektit
    3. Default-et e mëposhtme në klasën Settings

Importim nga moduli tjetër:
    from core.config import settings
    print(settings.DATABASE_URL)
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ---------- Aplikacioni ----------
    APP_NAME: str = "Hermes Marketplace API"
    APP_VERSION: str = "0.9.1"
    APP_DESCRIPTION: str = (
        "Hermes — Marketplace për pjesë këmbimi makinash. "
        "Webservice që lidh shitësit me blerësit dhe automatizon transportin. "
        "Pjesë e Detyrës së Kursit AIS 2026."
    )
    DEBUG: bool = True

    # ---------- Database ----------
    # SQLite default — ndryshohet pa rikompiluar duke vendosur DATABASE_URL te .env
    DATABASE_URL: str = "sqlite:///./hermes.db"

    # ---------- API ----------
    API_V1_PREFIX: str = "/api/v1"

    # ---------- CORS ----------
    # Për prodhim, vendos domain-et specifike; "*" lejon çdo origjinë (vetëm për dev)
    CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Instancë e vetme që importohet kudo
settings = Settings()
