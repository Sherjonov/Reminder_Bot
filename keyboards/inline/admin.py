"""Admin paneli klaviaturalari (barcha tillarda)."""
from aiogram.types import InlineKeyboardMarkup

from keyboards.styles import DANGER, PRIMARY, SUCCESS, ibtn
from services.misc.i18n import t

from .callbacks import AdminCb, GroupCb

Markup = InlineKeyboardMarkup


def admin_kb(lang: str = "uz") -> Markup:
    return Markup(inline_keyboard=[
        [ibtn(t(lang, "admin_btn_stats"), AdminCb(action="stats").pack(), PRIMARY),
         ibtn(t(lang, "admin_btn_backup"), AdminCb(action="backup").pack())],
        [ibtn(t(lang, "admin_btn_broadcast"), AdminCb(action="broadcast").pack(), SUCCESS)],
    ])


def admin_back_kb(lang: str = "uz") -> Markup:
    return Markup(inline_keyboard=[[ibtn(t(lang, "t_back"), AdminCb(action="home").pack())]])


def broadcast_confirm_kb(lang: str = "uz") -> Markup:
    return Markup(inline_keyboard=[[
        ibtn(t(lang, "admin_btn_send"), AdminCb(action="bc_yes").pack(), SUCCESS),
        ibtn(t(lang, "t_cancel"), AdminCb(action="bc_no").pack(), DANGER),
    ]])


def group_list_kb(items: list[dict]) -> Markup:
    buttons = [ibtn(f"🗑 #{rem['id']}", GroupCb(action="del", id=rem["id"]).pack(), DANGER) for rem in items]
    rows = [buttons[i:i + 4] for i in range(0, len(buttons), 4)]
    return Markup(inline_keyboard=rows)
