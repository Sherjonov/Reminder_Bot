"""Har bir shaxsiy chat so'rovida foydalanuvchini bazadan topadi/yaratadi va `db_user` sifatida beradi."""
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from services.db_api import users as user_db


class UserContextMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        chat = data.get("event_chat")
        # Guruhlarda hamma a'zoni bazaga yozmaymiz — faqat shaxsiy chatda.
        if user and not user.is_bot and chat and chat.type == "private":
            data["db_user"] = await user_db.touch(user)
        return await handler(event, data)
