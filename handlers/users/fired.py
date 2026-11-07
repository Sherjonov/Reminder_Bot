"""Eslatma vaqti kelganda chiqqan xabar tugmalari: Bajarildi / Kechiktirish / Taymerni qayta ishga tushirish."""
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message

from filters import private_only
from keyboards.inline.callbacks import FireCb
from services.db_api import reminders as rem_db
from services.misc.constants import SNOOZE_MINUTES
from services.misc.formatting import fmt_clock, fmt_minutes
from services.misc.i18n import t
from services.misc.timeutils import get_tz

from .timer import start_timer

router = Router(name="fired")
private_only(router)


async def _finish(call: CallbackQuery, suffix: str) -> None:
    """Xabar matnini saqlagan holda tugmalarni olib tashlaydi va oxiriga belgi qo'shadi."""
    msg = call.message
    if not isinstance(msg, Message):
        return
    try:
        text = f"{msg.html_text}\n\n{suffix}" if suffix else msg.html_text
        await msg.edit_text(text, reply_markup=None)
    except TelegramBadRequest:
        pass


@router.callback_query(FireCb.filter())
async def on_fire_action(call: CallbackQuery, callback_data: FireCb, db_user: dict, lang: str) -> None:
    rem = await rem_db.get(callback_data.id)
    if not rem or rem["user_id"] != call.from_user.id:
        await _finish(call, "")
        await call.answer(t(lang, "rem_nf_short"), show_alert=True)
        return

    action = callback_data.action
    if action == "done":
        await rem_db.mark_done(rem["id"], call.from_user.id)
        await _finish(call, t(lang, "done_mark"))
        await call.answer(t(lang, "done_toast"))
    elif action == "snooze" and callback_data.value in SNOOZE_MINUTES:
        new = await rem_db.snooze(rem["id"], call.from_user.id, callback_data.value)
        if new is None:
            await call.answer(t(lang, "rem_nf_short"), show_alert=True)
            return
        clock = fmt_clock(new["remind_at"], get_tz(db_user["timezone"]))
        await _finish(call, t(lang, "snoozed_mark", dur=fmt_minutes(callback_data.value, lang), clock=clock))
        await call.answer(t(lang, "snoozed_toast"))
    elif action == "again" and rem["category"] == "timer" and rem["duration_min"]:
        await start_timer(call, db_user, lang, int(rem["duration_min"]))
        await call.answer(t(lang, "timer_again_toast"))
    else:  # ok
        await _finish(call, "")
        await call.answer()
