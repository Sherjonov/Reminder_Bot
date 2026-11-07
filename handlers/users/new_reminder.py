"""Yangi eslatma yaratish: tur -> matn -> vaqt -> tasdiqlash (takrorlanish shu yerda tanlanadi)."""
from __future__ import annotations

from datetime import datetime, time, timedelta, tzinfo

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from filters import private_only
from keyboards.inline.callbacks import CatCb, ConfirmCb, RepCb, WhenCb
from keyboards.inline.reminders import cancel_kb, categories_kb, confirm_kb, interval_kb, quick_time_kb
from services.db_api import reminders as rem_db
from services.flow import edit_or_send, send_new
from services.misc.constants import CATEGORY_EMOJI, MAX_ACTIVE_PER_USER, MAX_TEXT_LEN, MIN_LEAD_SECONDS, REPEAT_TYPES
from services.misc.formatting import category_name, esc, fmt_in, fmt_when, repeat_label
from services.misc.i18n import t
from services.misc.time_parser import parse_when
from services.misc.timeutils import get_tz, to_local, to_utc, utcnow
from states import NewReminder

router = Router(name="new_reminder")
private_only(router)


# ------------------------------------------------------------------ yordamchilar
def _is_future(dt: datetime) -> bool:
    return dt > utcnow() + timedelta(seconds=MIN_LEAD_SECONDS)


def _quick_target(key: str, tz: tzinfo) -> datetime | None:
    now = utcnow().replace(microsecond=0)
    if key == "m10":
        return now + timedelta(minutes=10)
    if key == "m30":
        return now + timedelta(minutes=30)
    if key == "h1":
        return now + timedelta(hours=1)
    local = to_local(now, tz)
    if key == "eve":
        target = datetime.combine(local.date(), time(20, 0), tzinfo=tz)
        if target <= local:
            target = datetime.combine(local.date() + timedelta(days=1), time(20, 0), tzinfo=tz)
        return to_utc(target)
    if key == "tom":
        return to_utc(datetime.combine(local.date() + timedelta(days=1), time(9, 0), tzinfo=tz))
    return None


def confirm_text(data: dict, tz: tzinfo, lang: str) -> str:
    category = data.get("category", "other")
    remind_at = datetime.fromisoformat(data["remind_at"])
    now = utcnow()
    return t(
        lang, "cf_card",
        emoji=CATEGORY_EMOJI.get(category, "🔔"), name=category_name(category, lang), text=esc(data["text"]),
        when=fmt_when(remind_at, tz, lang, now), in_=fmt_in((remind_at - now).total_seconds(), lang),
        repeat=repeat_label(data.get("repeat_type", "none"), data.get("repeat_value"), lang),
        note=t(lang, "cf_assumed") if data.get("assumed") else "",
    )


async def show_confirm(
    event: Message | CallbackQuery, state: FSMContext, db_user: dict, lang: str, *, edit: bool = False
) -> None:
    """Tasdiqlash kartochkasini ko'rsatadi (quick_add ham shu funksiyadan foydalanadi)."""
    data = await state.get_data()
    await state.set_state(NewReminder.confirm)
    text = confirm_text(data, get_tz(db_user["timezone"]), lang)
    markup = confirm_kb(lang, data.get("repeat_type", "none"), data.get("repeat_value"))
    if edit:
        await edit_or_send(event, text, markup)
    else:
        await send_new(event, text, markup)


# ------------------------------------------------------------------ 1. tur
async def begin(event: Message | CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await state.set_state(NewReminder.category)
    await send_new(event, t(lang, "nr_title"), categories_kb(lang))


@router.callback_query(CatCb.filter(), NewReminder.category)
async def pick_category(call: CallbackQuery, callback_data: CatCb, state: FSMContext, lang: str) -> None:
    key = callback_data.key if callback_data.key in CATEGORY_EMOJI and callback_data.key != "timer" else "other"
    await state.update_data(category=key, repeat_type="none", repeat_value=None, assumed=False)
    await state.set_state(NewReminder.text)
    await edit_or_send(
        call, t(lang, "nr_ask_text", emoji=CATEGORY_EMOJI[key], name=category_name(key, lang)), cancel_kb(lang)
    )
    await call.answer()


# ------------------------------------------------------------------ 2. matn
@router.message(NewReminder.text, F.text)
async def got_text(message: Message, state: FSMContext, lang: str) -> None:
    text = message.text.strip()
    if len(text) < 2:
        await message.answer(t(lang, "nr_text_short"))
        return
    if len(text) > MAX_TEXT_LEN:
        await message.answer(t(lang, "nr_text_long", n=len(text), max=MAX_TEXT_LEN))
        return
    await state.update_data(text=text)
    await state.set_state(NewReminder.when)
    await message.answer(t(lang, "when_prompt"), reply_markup=quick_time_kb(lang))


# ------------------------------------------------------------------ 3. vaqt
@router.callback_query(WhenCb.filter(), NewReminder.when)
async def quick_when(call: CallbackQuery, callback_data: WhenCb, state: FSMContext, db_user: dict, lang: str) -> None:
    target = _quick_target(callback_data.key, get_tz(db_user["timezone"]))
    if target is None:
        await call.answer()
        return
    await state.update_data(remind_at=target.isoformat(), assumed=False)
    await show_confirm(call, state, db_user, lang, edit=True)
    await call.answer()


@router.message(NewReminder.when, F.text)
async def typed_when(message: Message, state: FSMContext, db_user: dict, lang: str) -> None:
    result = parse_when(message.text, get_tz(db_user["timezone"]))
    if result is None:
        await message.answer(t(lang, "not_understood"))
        return
    if not _is_future(result.dt_utc):
        await message.answer(t(lang, "past_time"))
        return
    await state.update_data(remind_at=result.dt_utc.isoformat(), assumed=result.assumed_time)
    await show_confirm(message, state, db_user, lang)


# ------------------------------------------------------------------ 4. tasdiqlash
@router.callback_query(RepCb.filter(), NewReminder.confirm)
async def set_repeat(call: CallbackQuery, callback_data: RepCb, state: FSMContext, db_user: dict, lang: str) -> None:
    kind = callback_data.kind
    if kind == "interval" and callback_data.value == 0:
        await edit_or_send(call, t(lang, "interval_title"), interval_kb(lang))
    elif kind == "back":
        await show_confirm(call, state, db_user, lang, edit=True)
    elif kind in REPEAT_TYPES:
        value = callback_data.value if kind == "interval" and 0 < callback_data.value <= 24 * 60 else None
        if kind == "interval" and value is None:
            await call.answer()
            return
        await state.update_data(repeat_type=kind, repeat_value=value)
        await show_confirm(call, state, db_user, lang, edit=True)
    await call.answer()


@router.callback_query(ConfirmCb.filter(F.action == "time"), NewReminder.confirm)
async def change_time(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.set_state(NewReminder.when)
    await edit_or_send(call, t(lang, "when_prompt"), quick_time_kb(lang))
    await call.answer()


@router.callback_query(ConfirmCb.filter(F.action == "text"), NewReminder.confirm)
async def change_text(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    await state.set_state(NewReminder.edit_text)
    await edit_or_send(call, t(lang, "edit_text_prompt", text=esc(data.get("text", ""))), cancel_kb(lang))
    await call.answer()


@router.message(NewReminder.edit_text, F.text)
async def got_new_text(message: Message, state: FSMContext, db_user: dict, lang: str) -> None:
    text = message.text.strip()
    if not 2 <= len(text) <= MAX_TEXT_LEN:
        await message.answer(t(lang, "nr_text_range", max=MAX_TEXT_LEN))
        return
    await state.update_data(text=text)
    await show_confirm(message, state, db_user, lang)


@router.message(NewReminder.confirm, F.text)
async def typed_in_confirm(message: Message, state: FSMContext, db_user: dict, lang: str) -> None:
    """Tasdiqlash bosqichida yangi vaqt yozilsa — vaqtni almashtiramiz."""
    result = parse_when(message.text, get_tz(db_user["timezone"]))
    if result is None or not _is_future(result.dt_utc):
        await message.answer(t(lang, "confirm_hint"))
        return
    await state.update_data(remind_at=result.dt_utc.isoformat(), assumed=result.assumed_time)
    await show_confirm(message, state, db_user, lang)


@router.callback_query(ConfirmCb.filter(F.action == "save"), NewReminder.confirm)
async def save(call: CallbackQuery, state: FSMContext, db_user: dict, lang: str) -> None:
    data = await state.get_data()
    if not data.get("text") or not data.get("remind_at"):
        await state.clear()
        await call.answer(t(lang, "session_expired"), show_alert=True)
        return

    remind_at = datetime.fromisoformat(data["remind_at"])
    if not _is_future(remind_at):
        await call.answer(t(lang, "time_passed_alert"), show_alert=True)
        return
    user_id = call.from_user.id
    if await rem_db.count_active(user_id) >= MAX_ACTIVE_PER_USER:
        await call.answer(t(lang, "limit_reached", max=MAX_ACTIVE_PER_USER), show_alert=True)
        return

    tz = get_tz(db_user["timezone"])
    repeat_type = data.get("repeat_type", "none")
    repeat_value = data.get("repeat_value")
    if repeat_type == "monthly":
        repeat_value = to_local(remind_at, tz).day  # oyning shu kunida takrorlanadi

    category = data.get("category", "other")
    await rem_db.create(
        user_id=user_id, chat_id=user_id, text=data["text"], remind_at=remind_at, category=category,
        tz=db_user["timezone"], repeat_type=repeat_type, repeat_value=repeat_value,
    )
    await state.clear()

    lines = [
        t(lang, "saved_title"), "",
        f"{CATEGORY_EMOJI.get(category, '🔔')} <b>{category_name(category, lang)}</b>",
        esc(data["text"]), "",
        t(lang, "card_when", when=fmt_when(remind_at, tz, lang)),
    ]
    if repeat_type != "none":
        lines.append(t(lang, "card_repeat", repeat=repeat_label(repeat_type, repeat_value, lang)))
    lines += ["", f"⏳ {t(lang, 'saved_in', in_=fmt_in((remind_at - utcnow()).total_seconds(), lang))}"]
    await edit_or_send(call, "\n".join(lines))
    await call.answer(t(lang, "saved_toast"))


@router.callback_query(ConfirmCb.filter(F.action == "cancel"), StateFilter(NewReminder))
async def cancel(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await edit_or_send(call, t(lang, "cancelled"))
    await call.answer()
