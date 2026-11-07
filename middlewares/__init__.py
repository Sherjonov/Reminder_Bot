from aiogram import Dispatcher

from config import settings

from .language import LanguageMiddleware
from .throttling import ThrottlingMiddleware
from .user_context import UserContextMiddleware


def setup_middlewares(dp: Dispatcher) -> None:
    """Outer middleware — filtrlardan oldin ishlaydi. Tartib: spamdan himoya -> foydalanuvchi -> til."""
    throttle = ThrottlingMiddleware(rate=settings.throttle_rate)
    dp.message.outer_middleware(throttle)
    dp.callback_query.outer_middleware(throttle)

    user_ctx = UserContextMiddleware()
    dp.message.outer_middleware(user_ctx)
    dp.callback_query.outer_middleware(user_ctx)

    language = LanguageMiddleware()
    dp.message.outer_middleware(language)
    dp.callback_query.outer_middleware(language)


__all__ = ["LanguageMiddleware", "ThrottlingMiddleware", "UserContextMiddleware", "setup_middlewares"]
