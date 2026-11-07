"""Botning buyruqlar menyusini (chap pastdagi «/» tugmasi) o'rnatadi — uz / ru / en."""
from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import BotCommand, BotCommandScopeAllGroupChats, BotCommandScopeAllPrivateChats, BotCommandScopeChat

from config import settings
from services.misc.i18n import t

logger = logging.getLogger(__name__)

TARGETS = ((None, "uz"), ("uz", "uz"), ("ru", "ru"), ("en", "en"))


def user_commands(lang: str) -> list[BotCommand]:
    return [
        BotCommand(command="start", description=t(lang, "cmd_start")),
        BotCommand(command="yangi", description=t(lang, "cmd_new")),
        BotCommand(command="taymer", description=t(lang, "cmd_timer")),
        BotCommand(command="eslatmalar", description=t(lang, "cmd_list")),
        BotCommand(command="bugun", description=t(lang, "cmd_today")),
        BotCommand(command="xarajatlar", description=t(lang, "cmd_expenses")),
        BotCommand(command="sozlamalar", description=t(lang, "cmd_settings")),
        BotCommand(command="vaqt", description=t(lang, "cmd_time")),
        BotCommand(command="yordam", description=t(lang, "cmd_help")),
        BotCommand(command="bekor", description=t(lang, "cmd_cancel")),
    ]


def group_commands(lang: str) -> list[BotCommand]:
    return [
        BotCommand(command="eslat", description=t(lang, "cmd_group_remind")),
        BotCommand(command="eslatmalar", description=t(lang, "cmd_group_list")),
        BotCommand(command="yordam", description=t(lang, "cmd_help")),
    ]


async def set_default_commands(bot: Bot) -> None:
    for code, lang in TARGETS:
        try:
            await bot.set_my_commands(user_commands(lang), scope=BotCommandScopeAllPrivateChats(), language_code=code)
            await bot.set_my_commands(group_commands(lang), scope=BotCommandScopeAllGroupChats(), language_code=code)
        except TelegramAPIError as exc:
            logger.warning("Buyruqlarni o'rnatib bo'lmadi (%s): %s", code or "default", exc)
    for admin_id in settings.admins:
        try:
            commands = user_commands("uz") + [BotCommand(command="admin", description=t("uz", "cmd_admin"))]
            await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=admin_id))
        except TelegramAPIError as exc:  # admin hali botga /start bosmagan bo'lishi mumkin
            logger.info("Admin %s uchun buyruqlar o'rnatilmadi: %s", admin_id, exc)
