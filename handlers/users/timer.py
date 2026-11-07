"""Taymer: tayyor tugmalar yoki o'zingiz kiritgan vaqt."""
from __future__ import annotations

from datetime import timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from filters import private_only
from keyboards.inline.callbacks import TimerCb
from keyboards.inline.reminders import timer_custom_kb, timer_kb, timer_started_kb
from services.db_api import reminders as rem_db
from services.flow import edit_or_send, send_new
from services.misc.constants import MAX_ACTIVE_PER_USER, MAX_TIMER_MINUTES
from services.misc.formatting import fmt_minutes, fmt_when
from services.misc.i18n import t
from services.misc.time_parser import parse_duration
from services.misc.timeutils import get_tz, utcnow
from states import TimerState

router = Router(name="timer")
private_only(router)


async def show_timer(message: Message, lang: str) -> None:
    await message.answer(t(lang, "timer_menu"), reply_markup=timer_kb(lang))


async def start_timer(event: Message | CallbackQuery, db_user: dict, lang: str, minutes: int) -> None:
    """Taymerni yaratadi va tasdiqlovchi xabar ko'rsatadi."""
    user_id = db_user["user_id"]
    if await rem_db.count_active(user_id) >= MAX_ACTIVE_PER_USER:
        await send_new(event, t(lang, "limit_reached", max=MAX_ACTIVE_PER_USER))
        return
    tz = get_tz(db_user["timezone"])
    now = utcnow().replace(microsecond=0)
    end = now + timedelta(minutes=minutes)
    rem_id = await rem_db.create(
        user_id=user_id, chat_id=user_id, text=fmt_minutes(minutes, "uz"), remind_at=end, category="timer",
        tz=db_user["timezone"], duration_min=minutes,
    )
    text = t(lang, "timer_started", dur=fmt_minutes(minutes, lang), when=fmt_when(end, tz, lang, now))
    await edit_or_send(event, text, timer_started_kb(rem_id, lang))


@router.callback_query(TimerCb.filter(F.action == "start"))
async def on_start(call: CallbackQuery, callback_data: TimerCb, state: FSMContext, db_user: dict, lang: str) -> None:
    await state.clear()
    if not 1 <= callback_data.minutes <= MAX_TIMER_MINUTES:
        await call.answer()
        return
    await start_timer(call, db_user, lang, callback_data.minutes)
    await call.answer(t(lang, "timer_toast"))


@router.callback_query(TimerCb.filter(F.action == "custom"))
async def on_custom(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.set_state(TimerState.custom)
    await edit_or_send(call, t(lang, "timer_custom"), timer_custom_kb(lang))
    await call.answer()


@router.callback_query(TimerCb.filter(F.action == "menu"))
async def on_menu(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await edit_or_send(call, t(lang, "timer_menu"), timer_kb(lang))
    await call.answer()


@router.callback_query(TimerCb.filter(F.action == "cancel"))
async def on_cancel(call: CallbackQuery, callback_data: TimerCb, state: FSMContext, lang: str) -> None:
    await state.clear()
    if callback_data.id:
        await rem_db.delete(callback_data.id, call.from_user.id)
        await edit_or_send(call, t(lang, "timer_cancelled"))
    else:
        await edit_or_send(call, t(lang, "timer_menu"), timer_kb(lang))
    await call.answer()


@router.message(TimerState.custom, F.text)
async def custom_done(message: Message, state: FSMContext, db_user: dict, lang: str) -> None:
    delta = parse_duration(message.text)
    if delta is None or delta < timedelta(minutes=1):
        await message.answer(t(lang, "timer_bad"))
        return
    minutes = int(round(delta.total_seconds() / 60))
    if minutes > MAX_TIMER_MINUTES:
        await message.answer(t(lang, "timer_too_long"))
        return
    await state.clear()
    await start_timer(message, db_user, lang, minutes)
