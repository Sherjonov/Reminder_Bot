"""/start da yuboriladigan salomlashuv (rasm + matn + asosiy menyu) — foydalanuvchi tilida."""
from __future__ import annotations

import logging

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import FSInputFile, Message

from config import ASSETS_DIR
from keyboards.default import main_menu_kb
from services.misc.formatting import esc
from services.misc.i18n import t

logger = logging.getLogger(__name__)

_file_ids: dict[str, str] = {}  # rasm bir marta yuklangach, Telegram file_id si saqlanadi


async def send_welcome(message: Message, name: str, lang: str = "uz") -> None:
    caption = t(lang, "welcome", name=esc(name))
    keyboard = main_menu_kb(lang)
    photo = ASSETS_DIR / f"welcome_{lang}.jpg"
    if not photo.exists():
        photo = ASSETS_DIR / "welcome.jpg"
    key = photo.name
    try:
        if key in _file_ids:
            await message.answer_photo(_file_ids[key], caption=caption, reply_markup=keyboard)
            return
        if photo.exists():
            sent = await message.answer_photo(FSInputFile(photo), caption=caption, reply_markup=keyboard)
            if sent.photo:
                _file_ids[key] = sent.photo[-1].file_id
            return
    except TelegramBadRequest as exc:
        logger.warning("Salomlashuv rasmini yuborib bo'lmadi: %s", exc)
        _file_ids.pop(key, None)
    await message.answer(caption, reply_markup=keyboard)
