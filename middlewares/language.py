"""Foydalanuvchi tilini aniqlaydi va handlerlarga `lang` sifatida beradi.

Bot tili foydalanuvchi qaysi tilda yozayotganiga qarab AVTOMATIK o'zgaradi (o'zbekcha / русский / English).
Til o'zgarganda yangi tildagi asosiy menyu yuboriladi.
"""
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from keyboards.default import main_menu_kb
from services.db_api import users as user_db
from services.misc.i18n import DEFAULT_LANG, lang_from_telegram, t
from services.misc.langdetect import detect_language
from states import EditReminder, ExpenseState, NewReminder, SettingsState

# Bu bosqichlarda foydalanuvchi MAZMUN yozadi (eslatma matni, mahsulot nomi...) — til belgisi emas.
CONTENT_STATES = {
    NewReminder.text.state,
    NewReminder.edit_text.state,
    EditReminder.text.state,
    ExpenseState.adding.state,
    ExpenseState.edit_title.state,
    SettingsState.timezone.state,
}


class LanguageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        db_user = data.get("db_user")
        if db_user is None:
            data["lang"] = lang_from_telegram(user.language_code if user else None)
            return await handler(event, data)

        lang = db_user.get("language") or DEFAULT_LANG
        if isinstance(event, Message) and event.text and not event.text.startswith("/"):
            state = data.get("state")
            current = await state.get_state() if state is not None else None
            if current not in CONTENT_STATES:
                detected = detect_language(event.text)
                if detected and detected != lang:
                    await user_db.set_language(user.id, detected)
                    db_user["language"] = lang = detected
                    await event.answer(t(lang, "lang_changed"), reply_markup=main_menu_kb(lang))
        data["lang"] = lang
        return await handler(event, data)
