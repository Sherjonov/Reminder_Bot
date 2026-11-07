"""Eslatmalar ro'yxati, tafsilot, tahrirlash va o'chirish."""
from __future__ import annotations

from datetime import datetime, time, timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from filters import private_only
from keyboards.inline.callbacks import RemCb
from keyboards.inline.reminders import back_to_detail_kb, delete_confirm_kb, detail_kb, list_kb
from services.db_api import reminders as rem_db
from services.flow import edit_or_send
from services.misc.constants import MAX_TEXT_LEN, MIN_LEAD_SECONDS, PAGE_SIZE
from services.misc.formatting import esc, list_item_line, reminder_card
from services.misc.i18n import t
from services.misc.time_parser import parse_when
from services.misc.timeutils import get_tz, to_local, to_utc, utcnow
from states import EditReminder

from . import new_reminder

router = Router(name="my_reminders")
private_only(router)


# ------------------------------------------------------------------ ro'yxat
async def build_list(db_user: dict, lang: str, page: int = 0, scope: str = "a") -> tuple[str, InlineKeyboardMarkup]:
    tz = get_tz(db_user["timezone"])
    user_id = db_user["user_id"]
    now = utcnow()

    until = None
    if scope == "t":  # bugun — mahalliy yarim tungacha
        local = to_local(now, tz)
        until = to_utc(datetime.combine(local.date() + timedelta(days=1), time(0, 0), tzinfo=tz))

    total = await rem_db.count_active(user_id, until)
    pages = max(1, -(-total // PAGE_SIZE))
    page = min(max(page, 0), pages - 1)
    items = await rem_db.list_active(user_id, PAGE_SIZE, page * PAGE_SIZE, until)

    title = t(lang, "list_title_today" if scope == "t" else "list_title_all")
    if total == 0:
        empty = t(lang, "list_empty_today" if scope == "t" else "list_empty_all")
        text = f"{title}\n\n{empty}\n\n{t(lang, 'list_empty_hint')}"
    else:
        body = "\n\n".join(list_item_line(i, rem, tz, lang, now) for i, rem in enumerate(items, 1))
        text = f"{t(lang, 'list_count', title=title, total=total)}\n\n{body}"
        if pages > 1:
            text += f"\n\n<i>{t(lang, 'list_page', p=page + 1, n=pages)}</i>"
        text += f"\n\n<i>{t(lang, 'list_open_hint')}</i>"
    return text, list_kb(items, page, pages, lang, scope)


async def show_list(event: Message | CallbackQuery, db_user: dict, lang: str, page: int = 0, scope: str = "a") -> None:
    text, markup = await build_list(db_user, lang, page, scope)
    await edit_or_send(event, text, markup)


async def _load(call: CallbackQuery, rem_id: int, lang: str) -> dict | None:
    """Faqat o'z faol eslatmasini qaytaradi; topilmasa foydalanuvchiga aytadi."""
    rem = await rem_db.get(rem_id)
    if not rem or rem["user_id"] != call.from_user.id or rem["status"] != "active":
        await call.answer(t(lang, "rem_gone"), show_alert=True)
        return None
    return rem


@router.callback_query(RemCb.filter(F.action == "page"))
async def on_page(call: CallbackQuery, callback_data: RemCb, state: FSMContext, db_user: dict, lang: str) -> None:
    await state.clear()
    await show_list(call, db_user, lang, callback_data.page, callback_data.scope)
    await call.answer()


@router.callback_query(RemCb.filter(F.action == "noop"))
async def on_noop(call: CallbackQuery) -> None:
    await call.answer()


@router.callback_query(RemCb.filter(F.action == "new"))
async def on_new(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await call.answer()
    await new_reminder.begin(call, state, lang)


# ------------------------------------------------------------------ tafsilot
@router.callback_query(RemCb.filter(F.action == "open"))
async def on_open(call: CallbackQuery, callback_data: RemCb, state: FSMContext, db_user: dict, lang: str) -> None:
    await state.clear()
    rem = await _load(call, callback_data.id, lang)
    if rem is None:
        return
    tz = get_tz(db_user["timezone"])
    await edit_or_send(call, reminder_card(rem, tz, lang), detail_kb(rem, lang, callback_data.page, callback_data.scope))
    await call.answer()


# ------------------------------------------------------------------ matnni tahrirlash
@router.callback_query(RemCb.filter(F.action == "etext"))
async def on_edit_text(call: CallbackQuery, callback_data: RemCb, state: FSMContext, lang: str) -> None:
    rem = await _load(call, callback_data.id, lang)
    if rem is None:
        return
    await state.clear()
    await state.set_state(EditReminder.text)
    await state.update_data(rem_id=rem["id"], page=callback_data.page, scope=callback_data.scope)
    await edit_or_send(
        call, t(lang, "edit_text_prompt", text=esc(rem["text"])),
        back_to_detail_kb(rem["id"], lang, callback_data.page, callback_data.scope),
    )
    await call.answer()


@router.message(EditReminder.text, F.text)
async def edit_text_done(message: Message, state: FSMContext, db_user: dict, lang: str) -> None:
    data = await state.get_data()
    text = message.text.strip()
    if not 2 <= len(text) <= MAX_TEXT_LEN:
        await message.answer(t(lang, "nr_text_range", max=MAX_TEXT_LEN))
        return
    rem = await rem_db.get(data.get("rem_id", 0))
    if not rem or rem["user_id"] != message.from_user.id or rem["status"] != "active":
        await state.clear()
        await message.answer(t(lang, "rem_nf"))
        return
    await rem_db.update_text(rem["id"], text)
    await state.clear()
    rem["text"] = text
    await message.answer(
        t(lang, "text_updated", card=reminder_card(rem, get_tz(db_user["timezone"]), lang)),
        reply_markup=detail_kb(rem, lang, data.get("page", 0), data.get("scope", "a")),
    )


# ------------------------------------------------------------------ vaqtni tahrirlash
@router.callback_query(RemCb.filter(F.action == "etime"))
async def on_edit_time(call: CallbackQuery, callback_data: RemCb, state: FSMContext, lang: str) -> None:
    rem = await _load(call, callback_data.id, lang)
    if rem is None:
        return
    await state.clear()
    await state.set_state(EditReminder.when)
    await state.update_data(rem_id=rem["id"], page=callback_data.page, scope=callback_data.scope)
    await edit_or_send(
        call, t(lang, "edit_time_prompt"), back_to_detail_kb(rem["id"], lang, callback_data.page, callback_data.scope)
    )
    await call.answer()


@router.message(EditReminder.when, F.text)
async def edit_time_done(message: Message, state: FSMContext, db_user: dict, lang: str) -> None:
    data = await state.get_data()
    result = parse_when(message.text, get_tz(db_user["timezone"]))
    if result is None:
        await message.answer(t(lang, "not_understood"))
        return
    if result.dt_utc <= utcnow() + timedelta(seconds=MIN_LEAD_SECONDS):
        await message.answer(t(lang, "past_time"))
        return
    rem = await rem_db.get(data.get("rem_id", 0))
    if not rem or rem["user_id"] != message.from_user.id or rem["status"] != "active":
        await state.clear()
        await message.answer(t(lang, "rem_nf"))
        return

    if rem["repeat_type"] == "monthly":  # oyning yangi kuniga ko'chadi
        day = to_local(result.dt_utc, get_tz(rem["timezone"])).day
        await rem_db.update_time(rem["id"], result.dt_utc, repeat_value=day, keep_value=False)
    else:
        await rem_db.update_time(rem["id"], result.dt_utc)
    await state.clear()
    rem["remind_at"] = result.dt_utc
    await message.answer(
        t(lang, "time_updated", card=reminder_card(rem, get_tz(db_user["timezone"]), lang)),
        reply_markup=detail_kb(rem, lang, data.get("page", 0), data.get("scope", "a")),
    )


# ------------------------------------------------------------------ o'chirish
@router.callback_query(RemCb.filter(F.action == "del"))
async def on_delete(call: CallbackQuery, callback_data: RemCb, db_user: dict, lang: str) -> None:
    rem = await _load(call, callback_data.id, lang)
    if rem is None:
        return
    card = reminder_card(rem, get_tz(db_user["timezone"]), lang)
    await edit_or_send(
        call, t(lang, "del_confirm", card=card), delete_confirm_kb(rem["id"], lang, callback_data.page, callback_data.scope)
    )
    await call.answer()


@router.callback_query(RemCb.filter(F.action == "delyes"))
async def on_delete_yes(call: CallbackQuery, callback_data: RemCb, db_user: dict, lang: str) -> None:
    deleted = await rem_db.delete(callback_data.id, call.from_user.id)
    await call.answer(t(lang, "deleted_toast") if deleted else t(lang, "rem_nf_short"))
    await show_list(call, db_user, lang, callback_data.page, callback_data.scope)
