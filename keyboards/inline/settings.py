"""Sozlamalar klaviaturalari (barcha tillarda)."""
from aiogram.types import InlineKeyboardMarkup

from keyboards.styles import DANGER, PRIMARY, SUCCESS, ibtn
from services.misc.i18n import LANG_NAMES, LANGS, t
from services.misc.timeutils import TIMEZONES, tz_title

from .callbacks import SetCb

Markup = InlineKeyboardMarkup


def settings_kb(lang: str, digest_enabled: bool) -> Markup:
    return Markup(inline_keyboard=[
        [ibtn(t(lang, "sb_tz"), SetCb(action="tz").pack(), PRIMARY)],
        [ibtn(t(lang, "sb_clock"), SetCb(action="clock").pack())],
        [ibtn(t(lang, "sb_digest_on" if digest_enabled else "sb_digest_off"), SetCb(action="digest").pack(), SUCCESS if digest_enabled else None)],
        [ibtn(t(lang, "sb_lang"), SetCb(action="lang").pack())],
        [ibtn(t(lang, "sb_wipe"), SetCb(action="wipe").pack(), DANGER)],
    ])


def timezones_kb(lang: str = "uz") -> Markup:
    buttons = [ibtn(tz_title(iana, lang), SetCb(action="tzset", value=str(i)).pack()) for i, (iana, _) in enumerate(TIMEZONES)]
    rows = [buttons[0:1]] + [buttons[i:i + 2] for i in range(1, len(buttons), 2)]
    rows.append([ibtn(t(lang, "tz_custom_btn"), SetCb(action="tzcustom").pack())])
    rows.append([ibtn(t(lang, "t_back"), SetCb(action="back").pack())])
    return Markup(inline_keyboard=rows)


def language_kb(lang: str = "uz") -> Markup:
    buttons = [
        ibtn(("✓ " if code == lang else "") + LANG_NAMES[code], SetCb(action="langset", value=code).pack(), PRIMARY if code == lang else None)
        for code in LANGS
    ]
    return Markup(inline_keyboard=[buttons, [ibtn(t(lang, "t_back"), SetCb(action="back").pack())]])


def wipe_confirm_kb(lang: str = "uz") -> Markup:
    return Markup(inline_keyboard=[[
        ibtn(t(lang, "btn_wipe_yes"), SetCb(action="wipeyes").pack(), DANGER),
        ibtn(t(lang, "t_no"), SetCb(action="back").pack()),
    ]])


def back_to_settings_kb(lang: str = "uz") -> Markup:
    return Markup(inline_keyboard=[[ibtn(t(lang, "t_back"), SetCb(action="back").pack())]])


def custom_tz_kb(lang: str = "uz") -> Markup:
    return Markup(inline_keyboard=[[ibtn(t(lang, "t_back"), SetCb(action="tz").pack())]])


def time_kb(lang: str = "uz") -> Markup:
    return Markup(inline_keyboard=[[ibtn(t(lang, "sb_clock"), SetCb(action="clock").pack(), PRIMARY)]])
