"""Bazani SQL fayl ko'rinishida zaxiralash (data/backups/) va adminlarga yuborish.

Tiklash: avval services/db_api/schema.sql, keyin zaxira faylini HeidiSQL'da (yoki mysql orqali) ishga tushiring.
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import FSInputFile
from pymysql.converters import escape_item

from config import DATA_DIR, settings
from services.db_api import db
from services.misc.i18n import t
from services.misc.timeutils import utcnow

logger = logging.getLogger(__name__)

BACKUP_DIR = DATA_DIR / "backups"
TABLES = ("users", "reminders", "wallets", "expenses", "wallet_log", "rates")  # tashqi kalit tufayli users birinchi
CHUNK = 200


def _cleanup() -> None:
    files = sorted(BACKUP_DIR.glob("*.sql"))
    for old in files[: max(len(files) - settings.backup_keep, 0)]:
        old.unlink(missing_ok=True)


async def make_backup() -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = utcnow().strftime("%Y%m%d_%H%M%S")
    path = BACKUP_DIR / f"{settings.db_name}_{stamp}.sql"
    lines = [
        f"-- {settings.db_name} zaxirasi (UTC {stamp})",
        "-- Tiklash: avval schema.sql, so'ng shu fayl.",
        "SET NAMES utf8mb4;",
        "SET FOREIGN_KEY_CHECKS = 0;",
        "",
    ]
    for table in TABLES:
        rows = await db.fetchall(f"SELECT * FROM `{table}`")
        if not rows:
            continue
        columns = list(rows[0].keys())
        column_sql = ", ".join(f"`{c}`" for c in columns)
        for start in range(0, len(rows), CHUNK):
            values = ",\n".join(
                "(" + ", ".join(escape_item(row[c], "utf8mb4") for c in columns) + ")"
                for row in rows[start : start + CHUNK]
            )
            lines.append(f"REPLACE INTO `{table}` ({column_sql}) VALUES\n{values};\n")
    lines.append("SET FOREIGN_KEY_CHECKS = 1;")
    await asyncio.to_thread(path.write_text, "\n".join(lines), "utf-8")
    await asyncio.to_thread(_cleanup)
    return path


async def send_backup(bot: Bot, chat_ids: list[int] | tuple[int, ...]) -> Path:
    path = await make_backup()
    for chat_id in chat_ids:
        try:
            await bot.send_document(chat_id, FSInputFile(path), caption=t("uz", "admin_backup_caption", name=path.name))
        except TelegramAPIError as exc:
            logger.warning("Zaxirani %s ga yuborib bo'lmadi: %s", chat_id, exc)
    return path


class BackupService:
    """Har `BACKUP_INTERVAL_HOURS` soatda zaxira oladi va adminlarga yuboradi."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        if settings.backup_enabled and self._task is None:
            self._task = asyncio.create_task(self._run(), name="backup-service")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run(self) -> None:
        interval = settings.backup_interval_hours * 3600
        while True:
            await asyncio.sleep(interval)
            try:
                await send_backup(self.bot, settings.admins)
                logger.info("Zaxira olindi")
            except asyncio.CancelledError:
                raise
            except Exception:  # noqa: BLE001
                logger.exception("Zaxira olishda xatolik")
