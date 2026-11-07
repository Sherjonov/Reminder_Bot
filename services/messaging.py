"""Xabar yuborish: xatolarga chidamli yuborish va ommaviy xabar (broadcast)."""
from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Callable

from aiogram import Bot
from aiogram.exceptions import (
    TelegramAPIError,
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramRetryAfter,
)

from services.db_api import users as user_db

logger = logging.getLogger(__name__)

SEND_OK = "ok"
SEND_BLOCKED = "blocked"      # foydalanuvchi botni bloklagan / bot guruhdan chiqarilgan
SEND_BAD = "bad_request"      # chat topilmadi, matn noto'g'ri va hokazo — qayta urinish befoyda
SEND_RETRY = "retry"          # vaqtinchalik xato (tarmoq, Telegram serveri) — keyinroq qayta uriniladi


async def safe_send(bot: Bot, chat_id: int, text: str, **kwargs) -> str:
    """Xabar yuboradi va natijani matn kodi sifatida qaytaradi (hech qachon exception tashlamaydi)."""
    for attempt in range(3):
        try:
            await bot.send_message(chat_id, text, **kwargs)
            return SEND_OK
        except TelegramRetryAfter as exc:
            await asyncio.sleep(exc.retry_after + 1)
        except TelegramForbiddenError:
            return SEND_BLOCKED
        except TelegramBadRequest as exc:
            logger.warning("Xabar yuborilmadi (chat %s): %s", chat_id, exc)
            return SEND_BAD
        except (TelegramNetworkError, asyncio.TimeoutError) as exc:
            logger.warning("Tarmoq xatosi (chat %s): %s", chat_id, exc)
            await asyncio.sleep(2 * (attempt + 1))
        except TelegramAPIError as exc:
            logger.warning("Telegram xatosi (chat %s): %s", chat_id, exc)
            return SEND_RETRY
    return SEND_RETRY


ProgressCb = Callable[[int, int, int, int], Awaitable[None]]


async def broadcast(
    bot: Bot,
    user_ids: list[int],
    from_chat_id: int,
    message_id: int,
    on_progress: ProgressCb | None = None,
) -> tuple[int, int]:
    """Xabarni nusxalab hammaga yuboradi (matn, rasm, video — formati saqlanadi). (yuborildi, xato) qaytaradi."""
    sent = failed = 0
    total = len(user_ids)
    for index, uid in enumerate(user_ids, 1):
        for _ in range(2):
            try:
                await bot.copy_message(chat_id=uid, from_chat_id=from_chat_id, message_id=message_id)
                sent += 1
                break
            except TelegramRetryAfter as exc:
                await asyncio.sleep(exc.retry_after + 1)
            except TelegramForbiddenError:
                failed += 1
                await user_db.set_blocked(uid, True)
                break
            except TelegramAPIError:
                failed += 1
                break
        else:
            failed += 1
        await asyncio.sleep(0.05)  # Telegram limiti: soniyasiga ~30 ta xabar
        if on_progress and (index % 50 == 0 or index == total):
            await on_progress(index, total, sent, failed)
    return sent, failed
