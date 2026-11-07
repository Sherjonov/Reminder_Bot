"""Eslatmalar bilan ishlash uchun inline klaviaturalar (barcha tillarda)."""
from aiogram.types import InlineKeyboardMarkup

from keyboards.styles import DANGER, PRIMARY, SUCCESS, ibtn
from services.misc.constants import INTERVAL_HOURS, SNOOZE_MINUTES, TIMER_PRESETS, USER_CATEGORIES
from services.misc.formatting import category_label, fmt_minutes, repeat_label
from services.misc.i18n import t

from .callbacks import CatCb, ConfirmCb, FireCb, RemCb, RepCb, TimerCb, WhenCb

Markup = InlineKeyboardMarkup


def cancel_kb(lang: str = "uz") -> Markup:
    return Markup(inline_keyboard=[[ibtn(t(lang, "t_cancel"), ConfirmCb(action="cancel").pack(), DANGER)]])


def categories_kb(lang: str = "uz") -> Markup:
    buttons = [ibtn(category_label(key, lang), CatCb(key=key).pack()) for key in USER_CATEGORIES]
    return Markup(inline_keyboard=[
        buttons[0:2],
        buttons[2:4],
        buttons[4:5],
        [ibtn(t(lang, "t_cancel"), ConfirmCb(action="cancel").pack(), DANGER)],
    ])


def quick_time_kb(lang: str = "uz") -> Markup:
    return Markup(inline_keyboard=[
        [ibtn(t(lang, "qt_m10"), WhenCb(key="m10").pack()), ibtn(t(lang, "qt_m30"), WhenCb(key="m30").pack())],
        [ibtn(t(lang, "qt_h1"), WhenCb(key="h1").pack()), ibtn(t(lang, "qt_eve"), WhenCb(key="eve").pack())],
        [ibtn(t(lang, "qt_tom"), WhenCb(key="tom").pack())],
        [ibtn(t(lang, "t_cancel"), ConfirmCb(action="cancel").pack(), DANGER)],
    ])


def confirm_kb(lang: str = "uz", repeat_type: str = "none", repeat_value: int | None = None) -> Markup:
    def option(kind: str, label: str):
        selected = repeat_type == kind
        return ibtn(f"✓ {label}" if selected else label, RepCb(kind=kind).pack(), PRIMARY if selected else None)

    interval_selected = repeat_type == "interval"
    interval_text = f"✓ {repeat_label('interval', repeat_value, lang)}" if interval_selected else t(lang, "rb_interval")
    return Markup(inline_keyboard=[
        [option("none", t(lang, "rep_none")), option("daily", t(lang, "rep_daily"))],
        [option("weekly", t(lang, "rep_weekly")), option("monthly", t(lang, "rep_monthly"))],
        [option("weekdays", t(lang, "rb_weekdays")), option("yearly", t(lang, "rep_yearly"))],
        [ibtn(interval_text, RepCb(kind="interval", value=0).pack(), PRIMARY if interval_selected else None)],
        [ibtn(t(lang, "t_save"), ConfirmCb(action="save").pack(), SUCCESS)],
        [ibtn(t(lang, "btn_change_time"), ConfirmCb(action="time").pack()), ibtn(t(lang, "btn_text"), ConfirmCb(action="text").pack())],
        [ibtn(t(lang, "t_cancel"), ConfirmCb(action="cancel").pack(), DANGER)],
    ])


def interval_kb(lang: str = "uz") -> Markup:
    buttons = [ibtn(t(lang, "interval_btn", n=h), RepCb(kind="interval", value=h * 60).pack()) for h in INTERVAL_HOURS]
    return Markup(inline_keyboard=[
        buttons[0:3],
        buttons[3:6],
        [ibtn(t(lang, "t_back"), RepCb(kind="back").pack())],
    ])


# ------------------------------------------------------------------ ro'yxat va tafsilot
def list_kb(items: list[dict], page: int, pages: int, lang: str = "uz", scope: str = "a") -> Markup:
    rows = []
    numbers = [
        ibtn(str(i + 1), RemCb(action="open", id=rem["id"], page=page, scope=scope).pack())
        for i, rem in enumerate(items)
    ]
    if numbers:
        rows.append(numbers)
    if pages > 1:
        noop = RemCb(action="noop").pack()
        rows.append([
            ibtn("◀️", RemCb(action="page", page=page - 1, scope=scope).pack()) if page > 0 else ibtn("·", noop),
            ibtn(f"{page + 1}/{pages}", noop),
            ibtn("▶️", RemCb(action="page", page=page + 1, scope=scope).pack()) if page < pages - 1 else ibtn("·", noop),
        ])
    rows.append([ibtn(t(lang, "btn_new"), RemCb(action="new").pack(), PRIMARY)])
    return Markup(inline_keyboard=rows)


def detail_kb(rem: dict, lang: str = "uz", page: int = 0, scope: str = "a") -> Markup:
    rid = rem["id"]
    rows = []
    if rem["category"] != "timer":
        rows.append([
            ibtn(t(lang, "btn_edit_text"), RemCb(action="etext", id=rid, page=page, scope=scope).pack()),
            ibtn(t(lang, "btn_edit_time"), RemCb(action="etime", id=rid, page=page, scope=scope).pack()),
        ])
    rows.append([ibtn(t(lang, "btn_delete"), RemCb(action="del", id=rid, page=page, scope=scope).pack(), DANGER)])
    rows.append([ibtn(t(lang, "btn_to_list"), RemCb(action="page", page=page, scope=scope).pack())])
    return Markup(inline_keyboard=rows)


def delete_confirm_kb(rem_id: int, lang: str = "uz", page: int = 0, scope: str = "a") -> Markup:
    return Markup(inline_keyboard=[[
        ibtn(t(lang, "btn_del_yes"), RemCb(action="delyes", id=rem_id, page=page, scope=scope).pack(), DANGER),
        ibtn(t(lang, "t_no"), RemCb(action="open", id=rem_id, page=page, scope=scope).pack()),
    ]])


def back_to_detail_kb(rem_id: int, lang: str = "uz", page: int = 0, scope: str = "a") -> Markup:
    return Markup(inline_keyboard=[[
        ibtn(t(lang, "t_cancel"), RemCb(action="open", id=rem_id, page=page, scope=scope).pack(), DANGER)
    ]])


# ------------------------------------------------------------------ eslatma vaqti kelganda
def fired_kb(rem: dict, lang: str = "uz") -> Markup:
    rid = rem["id"]
    if rem["category"] == "timer":
        row = []
        minutes = rem.get("duration_min") or 0
        if minutes:
            row.append(ibtn(t(lang, "btn_timer_again", dur=fmt_minutes(minutes, lang, 2)), FireCb(action="again", id=rid).pack(), PRIMARY))
        row.append(ibtn(t(lang, "btn_ok"), FireCb(action="ok", id=rid).pack(), SUCCESS))
        return Markup(inline_keyboard=[row])
    snooze = [
        ibtn(
            t(lang, "btn_snooze_m", m=m) if m < 60 else t(lang, "btn_snooze_h", h=m // 60),
            FireCb(action="snooze", id=rid, value=m).pack(),
        )
        for m in SNOOZE_MINUTES
    ]
    return Markup(inline_keyboard=[
        [ibtn(t(lang, "btn_done"), FireCb(action="done", id=rid).pack(), SUCCESS)],
        snooze,
    ])


# ------------------------------------------------------------------ taymer
def timer_kb(lang: str = "uz") -> Markup:
    buttons = [
        ibtn(
            fmt_minutes(m, lang, 2) if m < 60 else t(lang, "timer_h", n=m // 60),
            TimerCb(action="start", minutes=m).pack(),
        )
        for m in TIMER_PRESETS
    ]
    return Markup(inline_keyboard=[
        buttons[0:3],
        buttons[3:6],
        [buttons[6], ibtn(t(lang, "btn_custom_time"), TimerCb(action="custom").pack(), PRIMARY)],
    ])


def timer_started_kb(rem_id: int, lang: str = "uz") -> Markup:
    return Markup(inline_keyboard=[[ibtn(t(lang, "btn_timer_stop"), TimerCb(action="cancel", id=rem_id).pack(), DANGER)]])


def timer_custom_kb(lang: str = "uz") -> Markup:
    return Markup(inline_keyboard=[[ibtn(t(lang, "t_back"), TimerCb(action="menu").pack())]])
