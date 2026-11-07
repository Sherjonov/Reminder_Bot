"""`users` jadvali bilan ishlash."""
from __future__ import annotations

from datetime import date, datetime, timedelta

from aiogram.types import User

from config import settings
from services.misc.i18n import lang_from_telegram
from services.misc.timeutils import utcnow

from .database import db


async def get(user_id: int) -> dict | None:
    return await db.fetchone("SELECT * FROM users WHERE user_id = %s", (user_id,))


async def touch(tg_user: User) -> dict:
    """Foydalanuvchini yaratadi yoki (kerak bo'lsa) yangilaydi; sozlamalari saqlanib qoladi."""
    now = utcnow()
    full_name = (tg_user.full_name or "")[:255]
    username = (tg_user.username or None)
    lang = tg_user.language_code

    row = await get(tg_user.id)
    if row is None:
        await db.execute(
            "INSERT INTO users (user_id, username, full_name, language_code, language, timezone, created_at, last_active) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE user_id = user_id",
            (tg_user.id, username, full_name, lang, lang_from_telegram(lang), settings.default_tz, now, now),
        )
        return await get(tg_user.id) or {}

    stale = (now - row["last_active"]) > timedelta(minutes=5)
    changed = row["username"] != username or row["full_name"] != full_name or bool(row["is_blocked"])
    if stale or changed:
        await db.execute(
            "UPDATE users SET username = %s, full_name = %s, language_code = %s, last_active = %s, is_blocked = 0 "
            "WHERE user_id = %s",
            (username, full_name, lang, now, tg_user.id),
        )
        row.update(username=username, full_name=full_name, language_code=lang, last_active=now, is_blocked=0)
    return row


async def set_language(user_id: int, lang: str) -> None:
    await db.execute("UPDATE users SET language = %s WHERE user_id = %s", (lang, user_id))


async def set_timezone(user_id: int, tz_name: str) -> None:
    await db.execute("UPDATE users SET timezone = %s WHERE user_id = %s", (tz_name, user_id))


async def set_digest(user_id: int, enabled: bool) -> None:
    await db.execute("UPDATE users SET digest_enabled = %s WHERE user_id = %s", (1 if enabled else 0, user_id))


async def set_digest_date(user_id: int, day: date) -> None:
    await db.execute("UPDATE users SET last_digest_date = %s WHERE user_id = %s", (day, user_id))


async def set_blocked(user_id: int, blocked: bool) -> None:
    await db.execute("UPDATE users SET is_blocked = %s WHERE user_id = %s", (1 if blocked else 0, user_id))


async def digest_candidates() -> list[dict]:
    return await db.fetchall(
        "SELECT user_id, timezone, language, last_digest_date FROM users WHERE digest_enabled = 1 AND is_blocked = 0"
    )


async def all_ids(only_active: bool = True) -> list[int]:
    sql = "SELECT user_id FROM users" + (" WHERE is_blocked = 0" if only_active else "")
    return [row["user_id"] for row in await db.fetchall(sql)]


async def delete(user_id: int) -> None:
    """Foydalanuvchi va uning barcha eslatmalarini o'chiradi (FK: ON DELETE CASCADE)."""
    await db.execute("DELETE FROM users WHERE user_id = %s", (user_id,))


async def count_since(since: datetime) -> int:
    row = await db.fetchone("SELECT COUNT(*) AS c FROM users WHERE last_active >= %s", (since,))
    return int(row["c"]) if row else 0
