"""Admin ekanini tekshiruvchi filtr (ID lar .env dagi ADMINS dan olinadi)."""
from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from config import settings


class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user = event.from_user
        return bool(user and user.id in settings.admins)
