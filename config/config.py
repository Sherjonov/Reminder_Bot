"""Loyiha sozlamalari. Barcha qiymatlar .env faylidan o'qiladi."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"

load_dotenv(BASE_DIR / ".env")


def _str(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _int(name: str, default: int) -> int:
    try:
        return int(_str(name, str(default)))
    except ValueError:
        return default


def _float(name: str, default: float) -> float:
    try:
        return float(_str(name, str(default)))
    except ValueError:
        return default


def _bool(name: str, default: bool) -> bool:
    raw = _str(name)
    if not raw:
        return default
    return raw.lower() in {"1", "true", "yes", "on", "ha"}


def _admins(raw: str) -> tuple[int, ...]:
    ids: list[int] = []
    for part in raw.replace(";", ",").split(","):
        part = part.strip()
        if part.lstrip("-").isdigit():
            ids.append(int(part))
    return tuple(ids)


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admins: tuple[int, ...]

    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    default_tz: str
    scheduler_tick: int      # eslatmalar necha soniyada bir tekshiriladi
    throttle_rate: float     # bir foydalanuvchining so'rovlari orasidagi minimal masofa (soniya)
    digest_hour: int         # "Kunlik xulosa" yuboriladigan mahalliy soat
    set_bot_profile: bool    # ishga tushganda botning tavsif matnlarini yangilash

    backup_enabled: bool
    backup_interval_hours: int
    backup_keep: int

    health_enabled: bool
    health_host: str
    health_port: int

    log_level: str

    @property
    def token_ok(self) -> bool:
        token = self.bot_token
        return bool(token) and ":" in token and "YOUR_BOT_TOKEN" not in token.upper()


settings = Settings(
    bot_token=_str("BOT_TOKEN"),
    admins=_admins(_str("ADMINS")),
    db_host=_str("DB_HOST", "127.0.0.1"),
    db_port=_int("DB_PORT", 3306),
    db_user=_str("DB_USER", "root"),
    db_password=os.getenv("DB_PASSWORD", ""),
    db_name=_str("DB_NAME", "reminder_bot"),
    default_tz=_str("DEFAULT_TZ", "Asia/Tashkent"),
    scheduler_tick=max(_int("SCHEDULER_TICK", 10), 3),
    throttle_rate=_float("THROTTLE_RATE", 0.5),
    digest_hour=min(max(_int("DIGEST_HOUR", 8), 0), 20),
    set_bot_profile=_bool("SET_BOT_PROFILE", True),
    backup_enabled=_bool("BACKUP_ENABLED", True),
    backup_interval_hours=max(_int("BACKUP_INTERVAL_HOURS", 24), 1),
    backup_keep=max(_int("BACKUP_KEEP", 7), 1),
    health_enabled=_bool("HEALTH_SERVER", True),
    health_host=_str("HEALTH_HOST", "0.0.0.0"),
    health_port=_int("PORT", _int("HEALTH_PORT", 8080)),
    log_level=_str("LOG_LEVEL", "INFO").upper(),
)
