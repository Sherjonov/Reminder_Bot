"""Xarajatlar: umumiy summa (pulim), xaridlar (mahsulot nomi + narxi), so'mda va $ da hisob.

Qanday ishlaydi:
  * «Umumiy summa» — foydalanuvchida hozir bor pul (so'mda). Uni istalgan vaqt o'zgartirish, unga pul qo'shish mumkin.
  * Xarid qo'shilganda (masalan «Non 5000») narx umumiy summadan avtomatik ayriladi.
  * Summa so'mda ko'rsatiladi, uning tagida dollardagi qiymati (CBU kursi bo'yicha).
"""
from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from filters import private_only
from keyboards.inline import finance as kb
from keyboards.inline.callbacks import FinCb
from services import finance as fs
from services.currency import currency
from services.flow import edit_or_send, send_new
from services.misc.formatting import esc, fmt_when, short
from services.misc.i18n import t
from services.misc.money import (
    Amount, ExpenseLine, fmt_rate, fmt_sum, fmt_usd, parse_amount, parse_expense_lines, to_uzs,
)
from services.misc.timeutils import get_tz
from states import ExpenseState

router = Router(name="expenses")
private_only(router)

MAX_LINES = 30
PAGE_SIZE = 5
_ZERO_RE = re.compile(r"^\s*0+\s*$")


# ------------------------------------------------------------------ yordamchilar
def _usd_line(amount: int, lang: str, prefix: str = "\n") -> str:
    usd = fmt_usd(amount, currency.rate)
    return f"{prefix}{t(lang, 'fin_l_usd', v=usd)}" if usd else ""


def _amount_to_uzs(parsed: Amount | None) -> tuple[int | None, str | None]:
    """Kiritilgan summani so'mga o'giradi. (so'm, xato kaliti)."""
    if parsed is None:
        return None, "fin_amount_bad"
    uzs = to_uzs(parsed, currency.rate)
    if uzs is None:
        return None, ("fin_usd_no_rate" if parsed.currency == "usd" and not currency.rate else "fin_amount_bad")
    return uzs, None


def _item_suffix(line: ExpenseLine) -> str:
    return f" (${line.amount.value})" if line.amount and line.amount.currency == "usd" else ""


async def home_text(user_id: int, tz, lang: str) -> str:
    s = await fs.summary(user_id, tz)
    rate = currency.rate
    lines = [t(lang, "fin_title"), ""]
    if s.wallet.is_set:
        lines.append(t(lang, "fin_l_balance", v=f"<b>{fmt_sum(s.wallet.balance, lang)}</b>"))
        usd = fmt_usd(s.wallet.balance, rate)
        if usd:
            lines.append(t(lang, "fin_l_usd", v=usd))
        if s.wallet.balance < 0:
            lines.append(t(lang, "fin_neg_warn"))
    else:
        lines.append(t(lang, "fin_l_balance", v=t(lang, "fin_unset")))
    spent_usd = fmt_usd(s.spent_total, rate)
    lines.append(t(lang, "fin_l_spent", v=f"<b>{fmt_sum(s.spent_total, lang)}</b>" + (f" (≈ {spent_usd})" if spent_usd else "")))
    lines.append(t(lang, "fin_l_count", n=s.count))
    lines.append(t(lang, "fin_l_today", v=fmt_sum(s.spent_today, lang)))
    lines.append(t(lang, "fin_l_month", v=fmt_sum(s.spent_month, lang)))
    lines.append("")
    if rate:
        day = currency.rate_date.strftime("%d.%m.%Y") if currency.rate_date else "—"
        lines.append(t(lang, "fin_l_rate", rate=fmt_rate(rate, lang), date=day))
    else:
        lines.append(t(lang, "fin_no_rate"))
    if not s.wallet.is_set:
        lines += ["", t(lang, "fin_hint_unset")]
    return "\n".join(lines)


async def show_home(event: Message | CallbackQuery, db_user: dict, lang: str, *, edit: bool = False) -> None:
    text = await home_text(db_user["user_id"], get_tz(db_user["timezone"]), lang)
    sender = edit_or_send if edit else send_new
    await sender(event, text, kb.home_kb(lang))


def _added_text(result: fs.AddResult, lang: str, suffixes: list[str] | None = None) -> str:
    suffixes = suffixes or [""] * len(result.expenses)
    lines = [t(lang, "fin_added_title")]
    for expense, suffix in zip(result.expenses, suffixes):
        lines.append(t(lang, "fin_item", name=esc(expense["title"]), amount=fmt_sum(expense["amount"], lang) + suffix))
    if len(result.expenses) > 1:
        lines += ["━━━━━━━━", t(lang, "fin_added_total", v=fmt_sum(result.total, lang))]
        usd = fmt_usd(result.total, currency.rate)
        if usd:
            lines.append(t(lang, "fin_l_usd", v=usd))
    lines.append("")
    if result.deducted:
        lines.append(t(lang, "fin_remaining", v=fmt_sum(result.wallet.balance, lang)))
        usd = fmt_usd(result.wallet.balance, currency.rate)
        if usd:
            lines.append(t(lang, "fin_l_usd", v=usd))
        if result.negative:
            lines.append(t(lang, "fin_neg_warn"))
    else:
        lines.append(t(lang, "fin_not_deducted"))
    return "\n".join(lines)


def _detail_text(expense: dict, tz, lang: str) -> str:
    return t(
        lang, "fin_detail", title=esc(expense["title"]), amount=fmt_sum(int(expense["amount"]), lang),
        usd=_usd_line(int(expense["amount"]), lang), when=fmt_when(expense["created_at"], tz, lang, weekday=False),
        note="" if expense["deducted"] else t(lang, "fin_nodeduct_note"),
    )


# ------------------------------------------------------------------ bosh ekran
@router.callback_query(FinCb.filter(F.action == "home"))
async def on_home(call: CallbackQuery, state: FSMContext, db_user: dict, lang: str) -> None:
    await state.clear()
    await show_home(call, db_user, lang, edit=True)
    await call.answer()


@router.callback_query(FinCb.filter(F.action == "noop"))
async def on_noop(call: CallbackQuery) -> None:
    await call.answer()


# ------------------------------------------------------------------ xarajat qo'shish rejimi
@router.callback_query(FinCb.filter(F.action == "add"))
async def on_add(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await state.set_state(ExpenseState.adding)
    await state.update_data(last_ids=[], pending_name=None)
    await edit_or_send(call, t(lang, "fin_add_prompt"), kb.add_mode_kb(lang))
    await call.answer()


@router.callback_query(FinCb.filter(F.action == "done"))
async def on_done(call: CallbackQuery, state: FSMContext, db_user: dict, lang: str) -> None:
    await state.clear()
    await show_home(call, db_user, lang, edit=True)
    await call.answer()


@router.message(ExpenseState.adding, F.text)
async def on_adding(message: Message, state: FSMContext, db_user: dict, lang: str) -> None:
    lines = parse_expense_lines(message.text, limit=MAX_LINES + 1)
    if len(lines) > MAX_LINES:
        await message.answer(t(lang, "fin_too_many", max=MAX_LINES))
        return
    if not lines:
        return

    data = await state.get_data()
    pending = data.get("pending_name")
    if len(lines) == 1:
        line = lines[0]
        if pending and line.amount is not None and not line.name:      # oldingi nom + endi narx
            lines = [ExpenseLine(pending, line.amount)]
        elif line.name and line.amount is None and not line.bad_amount:  # faqat nom — narxini so'raymiz
            await state.update_data(pending_name=line.name)
            await message.answer(t(lang, "fin_ask_price", name=esc(line.name)))
            return
        elif line.amount is not None and not line.name:               # faqat narx — nomi kerak
            await message.answer(t(lang, "fin_ask_name"))
            return

    items: list[tuple[str, int]] = []
    suffixes: list[str] = []
    problems: list[str] = []
    for line in lines:
        if not line.name or line.amount is None:
            problems.append(t(lang, "fin_line_bad", line=esc(short(line.name or "?", 40))))
            continue
        uzs, error = _amount_to_uzs(line.amount)
        if uzs is None:
            problems.append(t(lang, error or "fin_amount_bad"))
            continue
        if len(line.name) > fs.MAX_TITLE:
            problems.append(t(lang, "fin_name_long", max=fs.MAX_TITLE))
            continue
        items.append((line.name, uzs))
        suffixes.append(_item_suffix(line))

    if not items:
        await message.answer("\n".join(dict.fromkeys(problems[:3])) or t(lang, "fin_amount_bad"))
        return

    result = await fs.add_expenses(message.from_user.id, items)
    await state.update_data(last_ids=[e["id"] for e in result.expenses], pending_name=None)
    text = _added_text(result, lang, suffixes)
    if problems:
        text += "\n\n" + "\n".join(dict.fromkeys(problems[:3]))
    await message.answer(text, reply_markup=kb.add_mode_kb(lang, can_undo=True))


@router.callback_query(FinCb.filter(F.action == "undo"))
async def on_undo(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    ids = data.get("last_ids") or []
    if not ids:
        await call.answer(t(lang, "fin_undo_none"), show_alert=True)
        return
    wallet, _, removed = await fs.undo_expenses(call.from_user.id, ids)
    await state.update_data(last_ids=[])
    lines = [t(lang, "fin_undone", n=removed), ""]
    if wallet.is_set:
        lines.append(t(lang, "fin_remaining", v=fmt_sum(wallet.balance, lang)))
        usd = fmt_usd(wallet.balance, currency.rate)
        if usd:
            lines.append(t(lang, "fin_l_usd", v=usd))
    lines += ["", t(lang, "fin_add_prompt")]
    await edit_or_send(call, "\n".join(lines), kb.add_mode_kb(lang))
    await call.answer()


# ------------------------------------------------------------------ erkin matndan tezkor xarajat ("Non 5000")
async def offer_quick_expense(message: Message, state: FSMContext, lang: str) -> bool:
    """Oddiy matn "nom + narx" ko'rinishida bo'lsa, xarajat sifatida qo'shishni taklif qiladi."""
    lines = parse_expense_lines(message.text, limit=MAX_LINES)
    if not lines:
        return False
    items: list[tuple[str, int]] = []
    for line in lines:
        if line.bad_amount or line.amount is None or not line.name or not any(ch.isalpha() for ch in line.name):
            return False
        uzs, _ = _amount_to_uzs(line.amount)
        if uzs is None or len(line.name) > fs.MAX_TITLE:
            return False
        items.append((line.name, uzs))
    await state.set_state(ExpenseState.quick)
    await state.update_data(quick_items=items)
    listing = "\n".join(t(lang, "fin_item", name=esc(n), amount=fmt_sum(a, lang)) for n, a in items)
    total = sum(a for _, a in items)
    await message.answer(t(lang, "fin_quick_ask", items=listing, total=fmt_sum(total, lang)), reply_markup=kb.quick_confirm_kb(lang))
    return True


@router.callback_query(FinCb.filter(F.action == "qyes"), ExpenseState.quick)
async def on_quick_yes(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    items = [(name, amount) for name, amount in data.get("quick_items") or []]
    await state.clear()
    if not items:
        await call.answer(t(lang, "session_expired"), show_alert=True)
        return
    result = await fs.add_expenses(call.from_user.id, items)
    await edit_or_send(call, _added_text(result, lang), kb.home_back_kb(lang))
    await call.answer()


@router.callback_query(FinCb.filter(F.action == "qno"), ExpenseState.quick)
async def on_quick_no(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await edit_or_send(call, t(lang, "fin_quick_cancelled"))
    await call.answer()


# ------------------------------------------------------------------ xaridlar ro'yxati va tafsilot
async def show_list(event: Message | CallbackQuery, db_user: dict, lang: str, page: int = 0) -> None:
    tz = get_tz(db_user["timezone"])
    items, total, page = await fs.list_page(db_user["user_id"], page, PAGE_SIZE)
    pages = max(1, -(-total // PAGE_SIZE))
    title = t(lang, "fin_list_title", total=total)
    if total == 0:
        text = f"{title}\n\n{t(lang, 'fin_list_empty')}"
    else:
        body = "\n\n".join(
            t(lang, "fin_list_item", i=i, title=esc(short(item["title"], 40)), amount=fmt_sum(int(item["amount"]), lang),
              when=fmt_when(item["created_at"], tz, lang, weekday=False))
            for i, item in enumerate(items, 1)
        )
        text = f"{title}\n\n{body}\n\n{t(lang, 'fin_list_hint')}"
    await edit_or_send(event, text, kb.list_kb(items, page, pages, lang))


@router.callback_query(FinCb.filter(F.action == "list"))
async def on_list(call: CallbackQuery, callback_data: FinCb, state: FSMContext, db_user: dict, lang: str) -> None:
    await state.clear()
    await show_list(call, db_user, lang, callback_data.page)
    await call.answer()


async def _open_expense(call: CallbackQuery, expense_id: int, lang: str) -> dict | None:
    try:
        return await fs.get_expense(call.from_user.id, expense_id)
    except fs.NotFoundError:
        await call.answer(t(lang, "fin_not_found"), show_alert=True)
        return None


@router.callback_query(FinCb.filter(F.action == "open"))
async def on_open(call: CallbackQuery, callback_data: FinCb, state: FSMContext, db_user: dict, lang: str) -> None:
    await state.clear()
    expense = await _open_expense(call, callback_data.id, lang)
    if expense is None:
        return
    await edit_or_send(call, _detail_text(expense, get_tz(db_user["timezone"]), lang), kb.detail_kb(expense["id"], lang, callback_data.page))
    await call.answer()


@router.callback_query(FinCb.filter(F.action == "etitle"))
async def on_edit_title(call: CallbackQuery, callback_data: FinCb, state: FSMContext, lang: str) -> None:
    expense = await _open_expense(call, callback_data.id, lang)
    if expense is None:
        return
    await state.clear()
    await state.set_state(ExpenseState.edit_title)
    await state.update_data(exp_id=expense["id"], page=callback_data.page)
    await edit_or_send(call, t(lang, "fin_edit_title_prompt", v=esc(expense["title"])), kb.edit_cancel_kb(expense["id"], lang, callback_data.page))
    await call.answer()


@router.callback_query(FinCb.filter(F.action == "eprice"))
async def on_edit_price(call: CallbackQuery, callback_data: FinCb, state: FSMContext, lang: str) -> None:
    expense = await _open_expense(call, callback_data.id, lang)
    if expense is None:
        return
    await state.clear()
    await state.set_state(ExpenseState.edit_price)
    await state.update_data(exp_id=expense["id"], page=callback_data.page)
    await edit_or_send(
        call, t(lang, "fin_edit_price_prompt", v=fmt_sum(int(expense["amount"]), lang)),
        kb.edit_cancel_kb(expense["id"], lang, callback_data.page),
    )
    await call.answer()


async def _finish_edit(message: Message, state: FSMContext, db_user: dict, lang: str, **changes) -> None:
    data = await state.get_data()
    try:
        expense, _ = await fs.update_expense(message.from_user.id, data.get("exp_id", 0), **changes)
    except fs.NotFoundError:
        await state.clear()
        await message.answer(t(lang, "fin_not_found"))
        return
    await state.clear()
    detail = _detail_text(expense, get_tz(db_user["timezone"]), lang)
    await message.answer(t(lang, "fin_updated", detail=detail), reply_markup=kb.detail_kb(expense["id"], lang, data.get("page", 0)))


@router.message(ExpenseState.edit_title, F.text)
async def on_title_typed(message: Message, state: FSMContext, db_user: dict, lang: str) -> None:
    title = " ".join(message.text.split())
    if not title or len(title) > fs.MAX_TITLE:
        await message.answer(t(lang, "fin_name_long", max=fs.MAX_TITLE))
        return
    await _finish_edit(message, state, db_user, lang, title=title)


@router.message(ExpenseState.edit_price, F.text)
async def on_price_typed(message: Message, state: FSMContext, db_user: dict, lang: str) -> None:
    uzs, error = _amount_to_uzs(parse_amount(message.text))
    if uzs is None:
        await message.answer(t(lang, error or "fin_amount_bad"))
        return
    await _finish_edit(message, state, db_user, lang, amount=uzs)


@router.callback_query(FinCb.filter(F.action == "del"))
async def on_delete(call: CallbackQuery, callback_data: FinCb, db_user: dict, lang: str) -> None:
    expense = await _open_expense(call, callback_data.id, lang)
    if expense is None:
        return
    detail = _detail_text(expense, get_tz(db_user["timezone"]), lang)
    await edit_or_send(call, t(lang, "fin_del_confirm", detail=detail), kb.delete_confirm_kb(expense["id"], lang, callback_data.page))
    await call.answer()


@router.callback_query(FinCb.filter(F.action == "delyes"))
async def on_delete_yes(call: CallbackQuery, callback_data: FinCb, db_user: dict, lang: str) -> None:
    try:
        wallet, refunded = await fs.delete_expense(call.from_user.id, callback_data.id)
    except fs.NotFoundError:
        await call.answer(t(lang, "fin_not_found"), show_alert=True)
        return
    await call.answer(t(lang, "fin_deleted_toast"))
    await show_list(call, db_user, lang, callback_data.page)


# ------------------------------------------------------------------ umumiy summa va pul qo'shish
@router.callback_query(FinCb.filter(F.action == "set"))
async def on_set(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    wallet = await fs.get_wallet(call.from_user.id)
    current = fmt_sum(wallet.balance, lang) if wallet.is_set else t(lang, "fin_unset")
    await state.clear()
    await state.set_state(ExpenseState.set_total)
    await edit_or_send(call, t(lang, "fin_set_prompt", current=current), kb.home_back_kb(lang))
    await call.answer()


@router.message(ExpenseState.set_total, F.text)
async def on_set_typed(message: Message, state: FSMContext, lang: str) -> None:
    if _ZERO_RE.match(message.text):
        amount: int | None = 0
    else:
        amount, error = _amount_to_uzs(parse_amount(message.text))
        if amount is None:
            await message.answer(t(lang, error or "fin_amount_bad"))
            return
    wallet = await fs.set_total(message.from_user.id, amount)
    await state.clear()
    await message.answer(
        t(lang, "fin_set_done", v=f"<b>{fmt_sum(wallet.balance, lang)}</b>", usd=_usd_line(wallet.balance, lang)),
        reply_markup=kb.home_kb(lang),
    )


@router.callback_query(FinCb.filter(F.action == "topup"))
async def on_topup(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await state.set_state(ExpenseState.topup)
    await edit_or_send(call, t(lang, "fin_topup_prompt"), kb.home_back_kb(lang))
    await call.answer()


@router.message(ExpenseState.topup, F.text)
async def on_topup_typed(message: Message, state: FSMContext, lang: str) -> None:
    amount, error = _amount_to_uzs(parse_amount(message.text))
    if amount is None:
        await message.answer(t(lang, error or "fin_amount_bad"))
        return
    wallet = await fs.top_up(message.from_user.id, amount)
    await state.clear()
    await message.answer(
        t(lang, "fin_topup_done", amount=fmt_sum(amount, lang), v=fmt_sum(wallet.balance, lang), usd=_usd_line(wallet.balance, lang)),
        reply_markup=kb.home_kb(lang),
    )


# ------------------------------------------------------------------ tarix
@router.callback_query(FinCb.filter(F.action == "log"))
async def on_log(call: CallbackQuery, state: FSMContext, db_user: dict, lang: str) -> None:
    await state.clear()
    tz = get_tz(db_user["timezone"])
    rows = await fs.history(call.from_user.id, 10)
    if not rows:
        text = f"{t(lang, 'fin_log_title')}\n\n{t(lang, 'fin_log_empty')}"
    else:
        lines = []
        for row in rows:
            delta = int(row["delta"])
            lines.append(t(
                lang, "fin_log_line", when=fmt_when(row["created_at"], tz, lang, weekday=False),
                label=t(lang, f"fin_k_{row['kind']}"), delta=("+" if delta > 0 else "") + fmt_sum(delta, lang),
                balance=fmt_sum(int(row["balance_after"]), lang),
            ))
        text = f"{t(lang, 'fin_log_title')}\n\n" + "\n".join(lines)
    await edit_or_send(call, text, kb.home_back_kb(lang))
    await call.answer()


# ------------------------------------------------------------------ eskirgan tugmalar (bot qayta ishga tushgan bo'lsa)
@router.callback_query(FinCb.filter(F.action.in_({"qyes", "qno"})))
async def on_stale_quick(call: CallbackQuery, lang: str) -> None:
    await call.answer(t(lang, "session_expired"), show_alert=True)
