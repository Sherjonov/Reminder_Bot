"""Botning "Description" va "About" matnlarini o'rnatadi — har bir til uchun alohida (Telegram foydalanuvchi tiliga qarab ko'rsatadi)."""
from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from services.misc.i18n import t

logger = logging.getLogger(__name__)

# (language_code, matn tili): None — boshqa barcha tillar uchun standart (o'zbekcha)
TARGETS = ((None, "uz"), ("uz", "uz"), ("ru", "ru"), ("en", "en"))


async def setup_bot_profile(bot: Bot) -> None:
    """Faqat matn o'zgargan bo'lsa yangilaydi (Telegram limitiga tegmaslik uchun)."""
    for code, lang in TARGETS:
        try:
            short, desc = t(lang, "profile_short"), t(lang, "profile_desc")
            current = await bot.get_my_short_description(language_code=code)
            if current.short_description != short:
                await bot.set_my_short_description(short_description=short, language_code=code)
            current = await bot.get_my_description(language_code=code)
            if current.description != desc:
                await bot.set_my_description(description=desc, language_code=code)
        except TelegramAPIError as exc:
            logger.warning("Bot profilini yangilab bo'lmadi (%s): %s", code or "default", exc)
