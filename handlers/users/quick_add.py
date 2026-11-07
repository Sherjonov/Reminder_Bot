"""Erkin matndan eslatma yoki xarajat yaratish: «ertaga 9:00 da shifokorga borishni eslat», «Non 5000»."""
from datetime import timedelta

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message

from filters import private_only
from keyboards.default import main_menu_kb
from services.misc.constants import MAX_TEXT_LEN, MIN_LEAD_SECONDS
from services.misc.i18n import t
from services.misc.time_parser import guess_category, parse_when
from services.misc.timeutils import get_tz, utcnow

from .expenses import offer_quick_expense
from .new_reminder import show_confirm

router = Router(name="quick_add")
private_only(router)


@router.message(StateFilter(default_state), F.text, ~F.text.startswith("/"))
async def quick_add(message: Message, state: FSMContext, db_user: dict, lang: str) -> None:
    result = parse_when(message.text, get_tz(db_user["timezone"]), loose=False)
    if result is None:
        if await offer_quick_expense(message, state, lang):  # "Non 5000" kabi xarajat
            return
        await message.answer(t(lang, "unknown_text"), reply_markup=main_menu_kb(lang))
        return

    text = result.remainder
    if len(text) < 2:
        await message.answer(t(lang, "qa_no_text"))
        return
    if len(text) > MAX_TEXT_LEN:
        await message.answer(t(lang, "nr_text_long", n=len(text), max=MAX_TEXT_LEN))
        return
    if result.dt_utc <= utcnow() + timedelta(seconds=MIN_LEAD_SECONDS):
        await message.answer(t(lang, "past_time"))
        return

    await state.update_data(
        category=guess_category(text), text=text, remind_at=result.dt_utc.isoformat(),
        repeat_type="none", repeat_value=None, assumed=result.assumed_time,
    )
    await show_confirm(message, state, db_user, lang)
