"""Xarajatlar biznes-mantig'i: hamyon ("umumiy summa"), xaridlar, jurnal.

Qoidalar:
  * Barcha pul o'zgarishlari bitta tranzaksiyada bajariladi (hamyon qatori `FOR UPDATE` bilan qulflanadi),
    shuning uchun bir vaqtda kelgan so'rovlar ham qoldiqni buzmaydi.
  * Har bir o'zgarish `wallet_log` jurnaliga yoziladi (audit).
  * Umumiy summa kiritilmagan bo'lsa xarid yoziladi, lekin hech narsa ayrilmaydi (`deducted = 0`);
    keyin o'chirilsa yoki tahrirlansa ham qoldiqqa tegilmaydi.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, tzinfo
from typing import Sequence

from services.db_api import db
from services.db_api import finance as fin
from services.db_api.database import Transaction
from services.misc.money import MAX_UZS
from services.misc.timeutils import to_local, to_utc, utcnow

MAX_TITLE = 200


class FinanceError(Exception):
    """Biznes-qoida buzilganda."""


class NotFoundError(FinanceError):
    pass


class ValidationError(FinanceError):
    pass


@dataclass(frozen=True)
class Wallet:
    balance: int
    is_set: bool


@dataclass(frozen=True)
class AddResult:
    expenses: list[dict]
    total: int
    wallet: Wallet
    deducted: bool

    @property
    def negative(self) -> bool:
        return self.deducted and self.wallet.balance < 0


@dataclass(frozen=True)
class Summary:
    wallet: Wallet
    spent_total: int
    count: int
    spent_today: int
    spent_month: int


def _wallet(row: dict | None) -> Wallet:
    return Wallet(int(row["balance"]), bool(row["is_set"])) if row else Wallet(0, False)


def clean_title(title: str) -> str:
    title = " ".join(str(title).split())
    if not title:
        raise ValidationError("title_empty")
    if len(title) > MAX_TITLE:
        raise ValidationError("title_long")
    return title


def check_amount(amount: int, allow_zero: bool = False) -> int:
    if not isinstance(amount, int) or isinstance(amount, bool):
        raise ValidationError("amount_type")
    low = 0 if allow_zero else 1
    if not low <= amount <= MAX_UZS:
        raise ValidationError("amount_range")
    return amount


async def _locked_wallet(tx: Transaction, user_id: int, now: datetime) -> dict:
    await fin.ensure_wallet(tx, user_id, now)
    row = await fin.get_wallet(tx, user_id, lock=True)
    assert row is not None
    return row


# ---------------------------------------------------------------- hamyon
async def get_wallet(user_id: int) -> Wallet:
    return _wallet(await fin.get_wallet(db, user_id))


async def set_total(user_id: int, amount: int) -> Wallet:
    """Umumiy summani aniq qiymatga o'rnatadi (foydalanuvchi "hozir menda shuncha pul bor" deydi)."""
    check_amount(amount, allow_zero=True)

    async def work(tx: Transaction) -> Wallet:
        now = utcnow()
        row = await _locked_wallet(tx, user_id, now)
        old = int(row["balance"])
        await fin.save_wallet(tx, user_id, amount, True, now)
        await fin.add_log(tx, user_id, "set", amount - old, amount, None, None, now)
        return Wallet(amount, True)

    return await db.run_in_transaction(work)


async def top_up(user_id: int, amount: int) -> Wallet:
    check_amount(amount)

    async def work(tx: Transaction) -> Wallet:
        now = utcnow()
        row = await _locked_wallet(tx, user_id, now)
        balance = int(row["balance"]) + amount
        await fin.save_wallet(tx, user_id, balance, True, now)
        await fin.add_log(tx, user_id, "topup", amount, balance, None, None, now)
        return Wallet(balance, True)

    return await db.run_in_transaction(work)


# ---------------------------------------------------------------- xaridlar
async def add_expenses(user_id: int, items: Sequence[tuple[str, int]]) -> AddResult:
    """Bir yoki bir nechta xaridni qo'shadi va umumiy summadan ayiradi (hammasi bitta tranzaksiyada)."""
    if not items:
        raise ValidationError("empty")
    cleaned = [(clean_title(title), check_amount(amount)) for title, amount in items]

    async def work(tx: Transaction) -> AddResult:
        now = utcnow()
        row = await _locked_wallet(tx, user_id, now)
        balance, deduct = int(row["balance"]), bool(row["is_set"])
        created: list[dict] = []
        for title, amount in cleaned:
            expense_id = await fin.add_expense(tx, user_id, title, amount, deduct, now)
            if deduct:
                balance -= amount
                await fin.add_log(tx, user_id, "expense", -amount, balance, expense_id, title, now)
            created.append({"id": expense_id, "title": title, "amount": amount, "deducted": deduct, "created_at": now})
        if deduct:
            await fin.save_wallet(tx, user_id, balance, True, now)
        return AddResult(created, sum(a for _, a in cleaned), Wallet(balance, deduct), deduct)

    return await db.run_in_transaction(work)


async def update_expense(
    user_id: int, expense_id: int, *, title: str | None = None, amount: int | None = None
) -> tuple[dict, Wallet]:
    new_title = clean_title(title) if title is not None else None
    new_amount = check_amount(amount) if amount is not None else None

    async def work(tx: Transaction) -> tuple[dict, Wallet]:
        now = utcnow()
        row = await _locked_wallet(tx, user_id, now)
        expense = await fin.get_expense(tx, user_id, expense_id, lock=True)
        if expense is None:
            raise NotFoundError("expense")
        balance = int(row["balance"])
        final_title = new_title if new_title is not None else expense["title"]
        final_amount = new_amount if new_amount is not None else int(expense["amount"])
        if expense["deducted"] and final_amount != int(expense["amount"]):
            diff = int(expense["amount"]) - final_amount  # eski - yangi: musbat bo'lsa pul qaytadi
            balance += diff
            await fin.save_wallet(tx, user_id, balance, bool(row["is_set"]), now)
            await fin.add_log(tx, user_id, "edit", diff, balance, expense_id, final_title, now)
        await fin.update_expense(tx, expense_id, final_title, final_amount)
        expense.update(title=final_title, amount=final_amount)
        return expense, Wallet(balance, bool(row["is_set"]))

    return await db.run_in_transaction(work)


async def _remove(tx: Transaction, user_id: int, expense_id: int, balance: int, now: datetime) -> tuple[int, int, bool]:
    """Xaridni o'chiradi; ayrilgan bo'lsa pulni qaytaradi. (yangi qoldiq, qaytarilgan summa, topildimi)."""
    expense = await fin.get_expense(tx, user_id, expense_id, lock=True)
    if expense is None:
        return balance, 0, False
    refunded = 0
    if expense["deducted"]:
        refunded = int(expense["amount"])
        balance += refunded
        await fin.add_log(tx, user_id, "refund", refunded, balance, expense_id, expense["title"], now)
    await fin.delete_expense(tx, expense_id)
    return balance, refunded, True


async def delete_expense(user_id: int, expense_id: int) -> tuple[Wallet, int]:
    """Xaridni o'chiradi. (hamyon, qaytarilgan summa)."""
    wallet, refunded, removed = await undo_expenses(user_id, [expense_id])
    if not removed:
        raise NotFoundError("expense")
    return wallet, refunded


async def undo_expenses(user_id: int, expense_ids: Sequence[int]) -> tuple[Wallet, int, int]:
    """Bir nechta xaridni birdan bekor qiladi. (hamyon, qaytarilgan summa, o'chirilganlar soni)."""

    async def work(tx: Transaction) -> tuple[Wallet, int, int]:
        now = utcnow()
        row = await _locked_wallet(tx, user_id, now)
        balance = int(row["balance"])
        total_refund = removed = 0
        for expense_id in expense_ids:
            balance, refunded, found = await _remove(tx, user_id, expense_id, balance, now)
            total_refund += refunded
            removed += 1 if found else 0
        if total_refund:
            await fin.save_wallet(tx, user_id, balance, bool(row["is_set"]), now)
        return Wallet(balance, bool(row["is_set"])), total_refund, removed

    return await db.run_in_transaction(work)


# ---------------------------------------------------------------- o'qish
async def get_expense(user_id: int, expense_id: int) -> dict:
    expense = await fin.get_expense(db, user_id, expense_id)
    if expense is None:
        raise NotFoundError("expense")
    return expense


async def list_page(user_id: int, page: int, size: int) -> tuple[list[dict], int, int]:
    """(xaridlar, jami soni, to'g'rilangan sahifa raqami)."""
    total = await fin.count_expenses(db, user_id)
    pages = max(1, -(-total // size))
    page = min(max(page, 0), pages - 1)
    return await fin.list_expenses(db, user_id, size, page * size), total, page


async def summary(user_id: int, tz: tzinfo) -> Summary:
    now = utcnow()
    local = to_local(now, tz)
    day_start = to_utc(datetime.combine(local.date(), time(0, 0), tzinfo=tz))
    month_start = to_utc(datetime.combine(local.date().replace(day=1), time(0, 0), tzinfo=tz))
    spent_total, count = await fin.sum_expenses(db, user_id)
    spent_today, _ = await fin.sum_expenses(db, user_id, day_start)
    spent_month, _ = await fin.sum_expenses(db, user_id, month_start)
    return Summary(await get_wallet(user_id), spent_total, count, spent_today, spent_month)


async def history(user_id: int, limit: int = 10) -> list[dict]:
    return await fin.list_log(db, user_id, limit)
