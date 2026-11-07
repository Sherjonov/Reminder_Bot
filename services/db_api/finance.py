"""Xarajatlar moduli uchun SQL: hamyon, xaridlar, jurnal, valyuta kursi.

Funksiyalar birinchi argument sifatida `x` oladi — bu `db` (oddiy so'rov) yoki `tx` (tranzaksiya) bo'lishi mumkin.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any


# ---------------------------------------------------------------- hamyon
async def ensure_wallet(x: Any, user_id: int, now: datetime) -> None:
    await x.execute(
        "INSERT INTO wallets (user_id, balance, is_set, created_at, updated_at) VALUES (%s, 0, 0, %s, %s) "
        "ON DUPLICATE KEY UPDATE user_id = user_id",
        (user_id, now, now),
    )


async def get_wallet(x: Any, user_id: int, lock: bool = False) -> dict | None:
    sql = "SELECT * FROM wallets WHERE user_id = %s" + (" FOR UPDATE" if lock else "")
    return await x.fetchone(sql, (user_id,))


async def save_wallet(x: Any, user_id: int, balance: int, is_set: bool, now: datetime) -> None:
    await x.execute(
        "UPDATE wallets SET balance = %s, is_set = %s, updated_at = %s WHERE user_id = %s",
        (balance, 1 if is_set else 0, now, user_id),
    )


# ---------------------------------------------------------------- xaridlar
async def add_expense(x: Any, user_id: int, title: str, amount: int, deducted: bool, now: datetime) -> int:
    return await x.insert(
        "INSERT INTO expenses (user_id, title, amount, deducted, created_at) VALUES (%s, %s, %s, %s, %s)",
        (user_id, title, amount, 1 if deducted else 0, now),
    )


async def get_expense(x: Any, user_id: int, expense_id: int, lock: bool = False) -> dict | None:
    sql = "SELECT * FROM expenses WHERE id = %s AND user_id = %s" + (" FOR UPDATE" if lock else "")
    return await x.fetchone(sql, (expense_id, user_id))


async def update_expense(x: Any, expense_id: int, title: str, amount: int) -> None:
    await x.execute("UPDATE expenses SET title = %s, amount = %s WHERE id = %s", (title, amount, expense_id))


async def delete_expense(x: Any, expense_id: int) -> None:
    await x.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))


async def list_expenses(x: Any, user_id: int, limit: int, offset: int = 0) -> list[dict]:
    return await x.fetchall(
        "SELECT * FROM expenses WHERE user_id = %s ORDER BY created_at DESC, id DESC LIMIT %s OFFSET %s",
        (user_id, limit, offset),
    )


async def count_expenses(x: Any, user_id: int) -> int:
    row = await x.fetchone("SELECT COUNT(*) AS c FROM expenses WHERE user_id = %s", (user_id,))
    return int(row["c"]) if row else 0


async def sum_expenses(
    x: Any, user_id: int, start: datetime | None = None, end: datetime | None = None
) -> tuple[int, int]:
    """(jami summa, soni). start/end — UTC, end kiritilmaydi."""
    sql = "SELECT COALESCE(SUM(amount), 0) AS total, COUNT(*) AS n FROM expenses WHERE user_id = %s"
    args: list = [user_id]
    if start is not None:
        sql += " AND created_at >= %s"
        args.append(start)
    if end is not None:
        sql += " AND created_at < %s"
        args.append(end)
    row = await x.fetchone(sql, args)
    return (int(row["total"]), int(row["n"])) if row else (0, 0)


# ---------------------------------------------------------------- jurnal
async def add_log(
    x: Any, user_id: int, kind: str, delta: int, balance_after: int, expense_id: int | None,
    note: str | None, now: datetime,
) -> None:
    await x.execute(
        "INSERT INTO wallet_log (user_id, kind, delta, balance_after, expense_id, note, created_at) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (user_id, kind, delta, balance_after, expense_id, (note or None) and note[:200], now),
    )


async def list_log(x: Any, user_id: int, limit: int = 10) -> list[dict]:
    return await x.fetchall("SELECT * FROM wallet_log WHERE user_id = %s ORDER BY id DESC LIMIT %s", (user_id, limit))


# ---------------------------------------------------------------- kurs
async def get_rate(x: Any, code: str) -> dict | None:
    return await x.fetchone("SELECT * FROM rates WHERE code = %s", (code,))


async def save_rate(x: Any, code: str, rate: Decimal, rate_date: date | None, source: str, now: datetime) -> None:
    await x.execute(
        "INSERT INTO rates (code, rate, rate_date, source, fetched_at) VALUES (%s, %s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE rate = %s, rate_date = %s, source = %s, fetched_at = %s",
        (code, rate, rate_date, source, now, rate, rate_date, source, now),
    )


# ---------------------------------------------------------------- statistika (admin)
async def stats(x: Any) -> dict:
    wallets = await x.fetchone("SELECT COUNT(*) AS c FROM wallets WHERE is_set = 1")
    expenses = await x.fetchone("SELECT COUNT(*) AS c FROM expenses")
    return {"wallets": int(wallets["c"]) if wallets else 0, "expenses": int(expenses["c"]) if expenses else 0}
