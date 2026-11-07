"""Suhbat (flow) yordamchilari: xabarni tahrirlash yoki yangisini yuborish."""
from __future__ import annotations

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message, ReplyKeyboardMarkup


async def edit_or_send(
    event: Message | CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None,
):
    """Tugma bosilgan bo'lsa — xabarni tahrirlaydi (iloji bo'lmasa yangisini yuboradi); oddiy xabarga javob beradi."""
    if isinstance(event, CallbackQuery):
        msg = event.message
        if isinstance(msg, Message):
            try:
                return await msg.edit_text(text, reply_markup=reply_markup)
            except TelegramBadRequest as exc:
                if "message is not modified" in str(exc).lower():
                    return msg
                # rasmli xabar yoki juda eski xabar — pastda yangisini yuboramiz
        return await event.bot.send_message(event.from_user.id, text, reply_markup=reply_markup)
    return await event.answer(text, reply_markup=reply_markup)


async def send_new(
    event: Message | CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None,
):
    """Har doim yangi xabar yuboradi (Message ham, CallbackQuery ham uchun)."""
    if isinstance(event, CallbackQuery):
        return await event.bot.send_message(event.from_user.id, text, reply_markup=reply_markup)
    return await event.answer(text, reply_markup=reply_markup)
