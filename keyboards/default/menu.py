"""Asosiy menyu (pastdagi doimiy tugmalar) — foydalanuvchi tilida."""
from aiogram.types import ReplyKeyboardMarkup

from keyboards.styles import PRIMARY, SUCCESS, rbtn
from services.misc.i18n import t


def main_menu_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [rbtn(t(lang, "btn_new"), PRIMARY), rbtn(t(lang, "btn_timer"), PRIMARY)],
            [rbtn(t(lang, "btn_list")), rbtn(t(lang, "btn_today"))],
            [rbtn(t(lang, "btn_expenses"), SUCCESS), rbtn(t(lang, "btn_settings"))],
            [rbtn(t(lang, "btn_help"))],
        ],
        resize_keyboard=True,
        input_field_placeholder=t(lang, "placeholder"),
    )
