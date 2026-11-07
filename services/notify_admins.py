"""Adminlarni xabardor qilish (bot ishga tushdi / to'xtadi / xatolik) — admin uchun o'zbekcha."""
from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from config import settings
from services.misc.formatting import fmt_minutes, fmt_when
from services.misc.timeutils import get_clock_offset, get_tz, utcnow

logger = logging.getLogger(__name__)


async def notify_admins(bot: Bot, text: str) -> None:
    for admin_id in settings.admins:
        try:
            await bot.send_message(admin_id, text)
        except TelegramAPIError as exc:
            logger.info("Adminga (%s) xabar yuborilmadi: %s", admin_id, exc)


async def on_startup_notify(bot: Bot) -> None:
    now = utcnow()
    text = (
        "✅ <b>Eslatma Bot ishga tushdi</b>\n"
        f"🗄 Baza: <code>{settings.db_name}</code>\n"
        f"🕒 {fmt_when(now, get_tz(settings.default_tz), 'uz', now)}"
    )
    offset = int(get_clock_offset().total_seconds())
    if abs(offset) >= 60:
        sign = "+" if offset > 0 else "−"
        text += (
            f"\n\n⚠️ Kompyuter soati Telegram vaqtidan <b>{sign}{fmt_minutes(abs(offset) // 60, 'uz', 2)}</b> farq qiladi. "
            "Bot vaqtni <b>avtomatik to'g'riladi</b>, lekin Windows'da vaqt mintaqasini ham tekshiring: "
            "<i>(UTC+05:00) Toshkent</i>."
        )
    await notify_admins(bot, text)


async def on_shutdown_notify(bot: Bot) -> None:
    await notify_admins(bot, "🛑 <b>Eslatma Bot to'xtadi</b>")
