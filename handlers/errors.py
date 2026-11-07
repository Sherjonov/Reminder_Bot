"""Kutilmagan xatolarni ushlab, adminlarga xabar beradi va foydalanuvchiga muloyim javob qaytaradi."""
import logging
import traceback

from aiogram import Bot, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramNetworkError
from aiogram.types import ErrorEvent

from services.misc.formatting import esc
from services.misc.i18n import lang_from_telegram, t
from services.notify_admins import notify_admins

logger = logging.getLogger(__name__)
router = Router(name="errors")

_IGNORED_BAD_REQUEST = (
    "message is not modified",
    "query is too old",
    "query id is invalid",
    "message to edit not found",
    "message can't be edited",
)


@router.errors()
async def on_error(event: ErrorEvent, bot: Bot) -> bool:
    exc = event.exception
    if isinstance(exc, TelegramBadRequest) and any(part in str(exc).lower() for part in _IGNORED_BAD_REQUEST):
        return True
    if isinstance(exc, TelegramForbiddenError):  # foydalanuvchi botni bloklagan
        return True
    if isinstance(exc, TelegramNetworkError):
        logger.warning("Tarmoq xatosi: %s", exc)
        return True

    logger.error("Kutilmagan xatolik", exc_info=exc)
    trace = "".join(traceback.format_exception(exc))[-3000:]
    await notify_admins(bot, f"⚠️ <b>Xatolik</b>\n<pre>{esc(trace)}</pre>")

    update = event.update
    user = update.message.from_user if update.message else update.callback_query.from_user if update.callback_query else None
    lang = lang_from_telegram(user.language_code if user else None)
    try:
        if update.message:
            await update.message.answer(t(lang, "err_generic"))
        elif update.callback_query:
            await update.callback_query.answer(t(lang, "err_alert"), show_alert=True)
    except Exception:  # noqa: BLE001
        pass
    return True
