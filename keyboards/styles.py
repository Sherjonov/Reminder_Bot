"""Tugma ranglari.

Telegram Bot API 9.4+ tugmalarni ranglash imkonini beradi:
    PRIMARY — ko'k, SUCCESS — yashil, DANGER — qizil.
Eski aiogram versiyasida `style` maydoni bo'lmasa, tugmalar oddiy ko'rinishda chiqadi (xato bermaydi).
Tugma matnlari `services/misc/locales/` da (uz / ru / en).
"""
from __future__ import annotations

from aiogram.types import InlineKeyboardButton, KeyboardButton

PRIMARY = "primary"
SUCCESS = "success"
DANGER = "danger"

_INLINE_STYLE = "style" in InlineKeyboardButton.model_fields
_REPLY_STYLE = "style" in KeyboardButton.model_fields


def ibtn(text: str, callback_data: str | None = None, style: str | None = None, **kwargs) -> InlineKeyboardButton:
    """Inline tugma; `style` berilsa va qo'llab-quvvatlansa — rangli bo'ladi."""
    if style and _INLINE_STYLE:
        kwargs["style"] = style
    return InlineKeyboardButton(text=text, callback_data=callback_data, **kwargs)


def rbtn(text: str, style: str | None = None, **kwargs) -> KeyboardButton:
    """Reply (menyu) tugmasi."""
    if style and _REPLY_STYLE:
        kwargs["style"] = style
    return KeyboardButton(text=text, **kwargs)
