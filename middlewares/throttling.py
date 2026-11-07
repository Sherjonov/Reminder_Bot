"""Spamdan himoya: bir foydalanuvchi juda tez-tez bosmasligi uchun."""
import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from services.misc.i18n import lang_from_telegram, t


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate: float = 0.5) -> None:
        self.rate = rate
        self._last: dict[int, float] = {}
        self._warned: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None or self.rate <= 0:
            return await handler(event, data)

        now = time.monotonic()
        if now - self._last.get(user.id, 0.0) < self.rate:
            if isinstance(event, CallbackQuery):
                await event.answer()  # tugma "aylanib" qolmasligi uchun
            elif isinstance(event, Message) and now - self._warned.get(user.id, 0.0) > 5:
                self._warned[user.id] = now
                await event.answer(t(lang_from_telegram(user.language_code), "throttle"))
            return None

        self._last[user.id] = now
        if len(self._last) > 5000:  # xotira to'lib ketmasligi uchun eskilarini tozalaymiz
            limit = now - 60
            self._last = {k: v for k, v in self._last.items() if v > limit}
            self._warned = {k: v for k, v in self._warned.items() if v > limit}
        return await handler(event, data)
