"""Xarajatlar bo'limi klaviaturalari (barcha tillarda)."""
from aiogram.types import InlineKeyboardMarkup

from keyboards.styles import DANGER, PRIMARY, SUCCESS, ibtn
from services.misc.i18n import t

from .callbacks import FinCb

Markup = InlineKeyboardMarkup


def home_kb(lang: str = "uz") -> Markup:
    return Markup(inline_keyboard=[
        [ibtn(t(lang, "fb_add"), FinCb(action="add").pack(), SUCCESS)],
        [ibtn(t(lang, "fb_list"), FinCb(action="list").pack(), PRIMARY)],
        [ibtn(t(lang, "fb_set"), FinCb(action="set").pack())],
        [ibtn(t(lang, "fb_topup"), FinCb(action="topup").pack()), ibtn(t(lang, "fb_log"), FinCb(action="log").pack())],
    ])


def add_mode_kb(lang: str = "uz", can_undo: bool = False) -> Markup:
    row = []
    if can_undo:
        row.append(ibtn(t(lang, "fb_undo"), FinCb(action="undo").pack(), DANGER))
    row.append(ibtn(t(lang, "fb_done"), FinCb(action="done").pack(), SUCCESS))
    return Markup(inline_keyboard=[row])


def home_back_kb(lang: str = "uz") -> Markup:
    return Markup(inline_keyboard=[[ibtn(t(lang, "fb_home"), FinCb(action="home").pack())]])


def list_kb(items: list[dict], page: int, pages: int, lang: str = "uz") -> Markup:
    rows = []
    numbers = [ibtn(str(i + 1), FinCb(action="open", id=item["id"], page=page).pack()) for i, item in enumerate(items)]
    if numbers:
        rows.append(numbers)
    if pages > 1:
        noop = FinCb(action="noop").pack()
        rows.append([
            ibtn("◀️", FinCb(action="list", page=page - 1).pack()) if page > 0 else ibtn("·", noop),
            ibtn(f"{page + 1}/{pages}", noop),
            ibtn("▶️", FinCb(action="list", page=page + 1).pack()) if page < pages - 1 else ibtn("·", noop),
        ])
    rows.append([ibtn(t(lang, "fb_add"), FinCb(action="add").pack(), SUCCESS)])
    rows.append([ibtn(t(lang, "fb_home"), FinCb(action="home").pack())])
    return Markup(inline_keyboard=rows)


def detail_kb(expense_id: int, lang: str = "uz", page: int = 0) -> Markup:
    return Markup(inline_keyboard=[
        [ibtn(t(lang, "fb_edit_title"), FinCb(action="etitle", id=expense_id, page=page).pack()),
         ibtn(t(lang, "fb_edit_price"), FinCb(action="eprice", id=expense_id, page=page).pack())],
        [ibtn(t(lang, "fb_delete"), FinCb(action="del", id=expense_id, page=page).pack(), DANGER)],
        [ibtn(t(lang, "btn_to_list"), FinCb(action="list", page=page).pack())],
    ])


def delete_confirm_kb(expense_id: int, lang: str = "uz", page: int = 0) -> Markup:
    return Markup(inline_keyboard=[[
        ibtn(t(lang, "btn_del_yes"), FinCb(action="delyes", id=expense_id, page=page).pack(), DANGER),
        ibtn(t(lang, "t_no"), FinCb(action="open", id=expense_id, page=page).pack()),
    ]])


def edit_cancel_kb(expense_id: int, lang: str = "uz", page: int = 0) -> Markup:
    return Markup(inline_keyboard=[[ibtn(t(lang, "t_cancel"), FinCb(action="open", id=expense_id, page=page).pack(), DANGER)]])


def quick_confirm_kb(lang: str = "uz") -> Markup:
    return Markup(inline_keyboard=[[
        ibtn(t(lang, "fb_yes_add"), FinCb(action="qyes").pack(), SUCCESS),
        ibtn(t(lang, "fb_no"), FinCb(action="qno").pack(), DANGER),
    ]])
