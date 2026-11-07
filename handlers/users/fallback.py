"""Hech qaysi handler ushlamagan xabarlar va eskirgan tugmalar."""
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message

from filters import private_only
from keyboards.default import main_menu_kb
from services.misc.i18n import t

router = Router(name="user_fallback")
private_only(router)


@router.message(F.text.startswith("/"))
async def unknown_command(message: Message, lang: str) -> None:
    await message.answer(t(lang, "unknown_cmd"), reply_markup=main_menu_kb(lang))


@router.message(StateFilter(default_state))
async def unsupported_content(message: Message, lang: str) -> None:
    await message.answer(t(lang, "unsupported"), reply_markup=main_menu_kb(lang))


@router.message()
async def wrong_content_in_flow(message: Message, lang: str) -> None:
    await message.answer(t(lang, "wrong_in_flow"))


@router.callback_query()
async def stale_button(call: CallbackQuery, lang: str) -> None:
    await call.answer(t(lang, "stale_btn"), show_alert=True)
