"""Eslatma Bot — ishga tushirish nuqtasi.

Ishga tushirish:  python main.py
"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError, TelegramNetworkError, TelegramUnauthorizedError
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from handlers import setup_routers
from middlewares import setup_middlewares
from services.backup import BackupService
from services.bot_profile import setup_bot_profile
from services.currency import currency
from services.db_api import db
from services.health_server import HealthServer
from services.notify_admins import on_shutdown_notify, on_startup_notify
from services.scheduler import ReminderScheduler
from services.set_bot_commands import set_default_commands
from services.time_sync import time_sync

logger = logging.getLogger("main")


def setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)  # har bir update uchun log chiqmasin


async def main() -> None:
    setup_logging()

    if not settings.token_ok:
        logger.error("BOT_TOKEN topilmadi. .env faylida BOT_TOKEN=... qatorini to'ldiring (@BotFather dan oling).")
        sys.exit(1)

    try:
        await db.connect()
        await db.init_schema()
        await currency.load_cached()
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "MySQL ga ulanib bo'lmadi: %s\n.env dagi DB_HOST / DB_PORT / DB_USER / DB_PASSWORD / DB_NAME ni tekshiring "
            "va MySQL (XAMPP/HeidiSQL serveri) ishlayotganini tasdiqlang.",
            exc,
        )
        sys.exit(1)

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    setup_middlewares(dp)
    dp.include_router(setup_routers())

    await time_sync.sync_once()  # kompyuter soati noto'g'ri bo'lsa ham to'g'ri vaqt bilan ishlash uchun
    scheduler = ReminderScheduler(bot)
    backup = BackupService(bot)
    health = HealthServer()

    try:
        try:
            me = await bot.get_me()
        except TelegramUnauthorizedError:
            logger.error("BOT_TOKEN noto'g'ri. @BotFather dan olingan tokenni .env ga to'g'ri yozing.")
            sys.exit(1)
        except TelegramNetworkError as exc:
            logger.error("Telegram serveriga ulanib bo'lmadi: %s\nInternet aloqasini (yoki VPN/proksini) tekshiring.", exc)
            sys.exit(1)
        logger.info("Bot: @%s (baza: %s)", me.username, settings.db_name)

        await bot.delete_webhook(drop_pending_updates=False)
        await set_default_commands(bot)
        if settings.set_bot_profile:
            await setup_bot_profile(bot)

        await health.start()
        time_sync.start()
        currency.start()
        scheduler.start()
        backup.start()
        await on_startup_notify(bot)

        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        try:
            await on_shutdown_notify(bot)
        except TelegramAPIError:
            pass
        await scheduler.stop()
        await backup.stop()
        await time_sync.stop()
        await currency.stop()
        await health.stop()
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi")
