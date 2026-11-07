"""`reminders` jadvali bilan ishlash. Barcha vaqtlar — UTC (timezone'siz)."""
from __future__ import annotations

from datetime import datetime, timedelta

from services.misc.timeutils import DEFAULT_TZ, utcnow

from .database import db


async def create(
    *,
    user_id: int,
    chat_id: int,
    text: str,
    remind_at: datetime,
    category: str = "other",
    tz: str = DEFAULT_TZ,
    repeat_type: str = "none",
    repeat_value: int | None = None,
    duration_min: int | None = None,
    parent_id: int | None = None,
) -> int:
    return await db.insert(
        "INSERT INTO reminders (user_id, chat_id, category, text, remind_at, timezone, repeat_type, "
        "repeat_value, duration_min, parent_id, created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (user_id, chat_id, category, text, remind_at, tz, repeat_type, repeat_value, duration_min, parent_id, utcnow()),
    )


async def get(rem_id: int) -> dict | None:
    return await db.fetchone("SELECT * FROM reminders WHERE id = %s", (rem_id,))


# ---------------------------------------------------------------- ro'yxatlar
async def list_active(user_id: int, limit: int, offset: int = 0, until: datetime | None = None) -> list[dict]:
    sql = "SELECT * FROM reminders WHERE user_id = %s AND chat_id = %s AND status = 'active'"
    args: list = [user_id, user_id]
    if until is not None:
        sql += " AND remind_at < %s"
        args.append(until)
    sql += " ORDER BY remind_at ASC, id ASC LIMIT %s OFFSET %s"
    args += [limit, offset]
    return await db.fetchall(sql, args)


async def count_active(user_id: int, until: datetime | None = None) -> int:
    sql = "SELECT COUNT(*) AS c FROM reminders WHERE user_id = %s AND chat_id = %s AND status = 'active'"
    args: list = [user_id, user_id]
    if until is not None:
        sql += " AND remind_at < %s"
        args.append(until)
    row = await db.fetchone(sql, args)
    return int(row["c"]) if row else 0


async def list_between(user_id: int, start: datetime, end: datetime) -> list[dict]:
    return await db.fetchall(
        "SELECT * FROM reminders WHERE user_id = %s AND chat_id = %s AND status = 'active' "
        "AND remind_at >= %s AND remind_at < %s ORDER BY remind_at ASC",
        (user_id, user_id, start, end),
    )


async def list_chat(chat_id: int, limit: int = 10) -> list[dict]:
    return await db.fetchall(
        "SELECT r.*, u.full_name FROM reminders r JOIN users u ON u.user_id = r.user_id "
        "WHERE r.chat_id = %s AND r.status = 'active' ORDER BY r.remind_at ASC LIMIT %s",
        (chat_id, limit),
    )


async def count_chat(chat_id: int) -> int:
    row = await db.fetchone("SELECT COUNT(*) AS c FROM reminders WHERE chat_id = %s AND status = 'active'", (chat_id,))
    return int(row["c"]) if row else 0


# ---------------------------------------------------------------- tahrirlash
async def update_text(rem_id: int, text: str) -> None:
    await db.execute("UPDATE reminders SET text = %s WHERE id = %s", (text, rem_id))


async def update_time(rem_id: int, remind_at: datetime, repeat_value: int | None = None, keep_value: bool = True) -> None:
    if keep_value:
        await db.execute("UPDATE reminders SET remind_at = %s, status = 'active' WHERE id = %s", (remind_at, rem_id))
    else:
        await db.execute(
            "UPDATE reminders SET remind_at = %s, repeat_value = %s, status = 'active' WHERE id = %s",
            (remind_at, repeat_value, rem_id),
        )


async def delete(rem_id: int, user_id: int | None = None) -> bool:
    if user_id is None:
        return await db.execute("DELETE FROM reminders WHERE id = %s", (rem_id,)) > 0
    return await db.execute("DELETE FROM reminders WHERE id = %s AND user_id = %s", (rem_id, user_id)) > 0


# ---------------------------------------------------------------- rejalashtirgich uchun
async def due(now: datetime, limit: int = 100) -> list[dict]:
    return await db.fetchall(
        "SELECT r.*, u.full_name, u.username, u.language FROM reminders r JOIN users u ON u.user_id = r.user_id "
        "WHERE r.status = 'active' AND r.remind_at <= %s ORDER BY r.remind_at ASC LIMIT %s",
        (now, limit),
    )


async def mark_sent(rem_id: int, now: datetime) -> None:
    await db.execute(
        "UPDATE reminders SET status = 'sent', last_sent_at = %s, fired_count = fired_count + 1 WHERE id = %s",
        (now, rem_id),
    )


async def advance(rem_id: int, next_at: datetime, now: datetime) -> None:
    await db.execute(
        "UPDATE reminders SET remind_at = %s, last_sent_at = %s, fired_count = fired_count + 1 WHERE id = %s",
        (next_at, now, rem_id),
    )


async def mark_failed(rem_id: int) -> None:
    await db.execute("UPDATE reminders SET status = 'failed' WHERE id = %s", (rem_id,))


async def fail_all_for_chat(chat_id: int) -> int:
    return await db.execute("UPDATE reminders SET status = 'failed' WHERE chat_id = %s AND status = 'active'", (chat_id,))


# ---------------------------------------------------------------- bajarildi / kechiktirish
async def mark_done(rem_id: int, user_id: int) -> bool:
    """Bir martalik eslatmani 'bajarildi' qiladi. Takrorlanuvchi eslatma o'z jadvalida davom etadi."""
    return (
        await db.execute(
            "UPDATE reminders SET status = 'done' WHERE id = %s AND user_id = %s AND repeat_type = 'none'",
            (rem_id, user_id),
        )
        > 0
    )


async def snooze(rem_id: int, user_id: int, minutes: int) -> dict | None:
    """Eslatmani `minutes` daqiqaga kechiktiradi. Takrorlanuvchi bo'lsa — alohida bir martalik nusxa yaratadi."""
    rem = await get(rem_id)
    if not rem or rem["user_id"] != user_id:
        return None
    new_at = utcnow().replace(microsecond=0) + timedelta(minutes=minutes)
    if rem["repeat_type"] == "none":
        await db.execute("UPDATE reminders SET status = 'active', remind_at = %s WHERE id = %s", (new_at, rem_id))
        rem.update(status="active", remind_at=new_at)
        return rem
    new_id = await create(
        user_id=rem["user_id"], chat_id=rem["chat_id"], text=rem["text"], remind_at=new_at,
        category=rem["category"], tz=rem["timezone"], parent_id=rem_id,
    )
    return await get(new_id)


# ---------------------------------------------------------------- tozalash va statistika
async def purge_old(before: datetime) -> int:
    return await db.execute(
        "DELETE FROM reminders WHERE status IN ('sent', 'done', 'failed') AND COALESCE(last_sent_at, created_at) < %s",
        (before,),
    )


async def stats() -> dict:
    now = utcnow()
    users = await db.fetchone(
        "SELECT COUNT(*) AS total, COALESCE(SUM(is_blocked = 1), 0) AS blocked, "
        "COALESCE(SUM(last_active >= %s), 0) AS active7, COALESCE(SUM(digest_enabled = 1), 0) AS digest "
        "FROM users",
        (now - timedelta(days=7),),
    ) or {}
    by_status = {row["status"]: int(row["c"]) for row in await db.fetchall(
        "SELECT status, COUNT(*) AS c FROM reminders GROUP BY status"
    )}
    created_24h = await db.fetchone("SELECT COUNT(*) AS c FROM reminders WHERE created_at >= %s", (now - timedelta(days=1),))
    next_24h = await db.fetchone(
        "SELECT COUNT(*) AS c FROM reminders WHERE status = 'active' AND remind_at < %s", (now + timedelta(days=1),)
    )
    return {
        "users_total": int(users.get("total", 0)),
        "users_blocked": int(users.get("blocked", 0)),
        "users_active7": int(users.get("active7", 0)),
        "users_digest": int(users.get("digest", 0)),
        "by_status": by_status,
        "created_24h": int(created_24h["c"]) if created_24h else 0,
        "next_24h": int(next_24h["c"]) if next_24h else 0,
    }
