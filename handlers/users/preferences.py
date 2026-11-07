"""Sozlamalar: vaqt mintaqasi, soatni moslash, til, kunlik xulosa, ma'lumotlarni o'chirish."""
from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import settings
from filters import private_only
from keyboards.default import main_menu_kb
from keyboards.inline.callbacks import SetCb
from keyboards.inline.settings import (
    back_to_settings_kb, custom_tz_kb, language_kb, settings_kb, time_kb, timezones_kb, wipe_confirm_kb,
)
from services.db_api import users as user_db
from services.flow import edit_or_send, send_new
from services.misc.formatting import fmt_clock, fmt_minutes, fmt_when
from services.misc.i18n import LANG_NAMES, LANGS, t
from services.misc.timeutils import (
    TIMEZONES, get_clock_offset, get_tz, offset_from_local_clock, tz_from_input, tz_title, utc_offset_minutes,
    utcnow, zone_for_offset_minutes,
)
from services.time_sync import time_sync
from states import SettingsState

router = Router(name="preferences")
private_only(router)

_CLOCK_RE = re.compile(r"^\s*(\d{1,2})\s*[:.]\s*(\d{2})\s*(am|pm)?\s*$", re.IGNORECASE)


def settings_text(db_user: dict, lang: str) -> str:
    tz = get_tz(db_user["timezone"])
    digest = (
        t(lang, "set_digest_on", hour=f"{settings.digest_hour:02d}") if db_user["digest_enabled"] else t(lang, "set_digest_off")
    )
    return t(
        lang, "set_text", tz=tz_title(db_user["timezone"], lang), now=fmt_clock(utcnow(), tz),
        digest=digest, language=LANG_NAMES.get(lang, lang),
    )


async def show_settings(event: Message | CallbackQuery, db_user: dict, lang: str) -> None:
    await edit_or_send(event, settings_text(db_user, lang), settings_kb(lang, bool(db_user["digest_enabled"])))


async def show_time(message: Message, db_user: dict, lang: str) -> None:
    """/vaqt — foydalanuvchining hozirgi vaqti va vaqt mintaqasi (admin uchun qo'shimcha texnik ma'lumot)."""
    tz = get_tz(db_user["timezone"])
    now = utcnow()
    text = t(lang, "time_cmd", now=fmt_when(now, tz, lang, now), tz=tz_title(db_user["timezone"], lang))
    if message.from_user.id in settings.admins:
        seconds = int(get_clock_offset().total_seconds())
        sign = "+" if seconds >= 0 else "−"
        text += t(
            lang, "time_cmd_admin",
            offset=f"{sign}{fmt_minutes(abs(seconds) // 60, lang)}" if seconds else "0",
            source=(time_sync.source or "—"), utc=now.strftime("%Y-%m-%d %H:%M:%S"),
        )
    await message.answer(text, reply_markup=time_kb(lang))


async def _fresh(user_id: int, fallback: dict) -> dict:
    return await user_db.get(user_id) or fallback


@router.callback_query(SetCb.filter(F.action == "back"))
async def on_back(call: CallbackQuery, state: FSMContext, db_user: dict, lang: str) -> None:
    await state.clear()
    await show_settings(call, await _fresh(call.from_user.id, db_user), lang)
    await call.answer()


# ------------------------------------------------------------------ vaqt mintaqasi
@router.callback_query(SetCb.filter(F.action == "tz"))
async def on_tz(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await edit_or_send(call, t(lang, "tz_pick"), timezones_kb(lang))
    await call.answer()


@router.callback_query(SetCb.filter(F.action == "tzset"))
async def on_tz_set(call: CallbackQuery, callback_data: SetCb, db_user: dict, lang: str) -> None:
    try:
        iana, _ = TIMEZONES[int(callback_data.value)]
    except (ValueError, IndexError):
        await call.answer()
        return
    await user_db.set_timezone(call.from_user.id, iana)
    await show_settings(call, await _fresh(call.from_user.id, db_user), lang)
    await call.answer(f"✅ {tz_title(iana, lang)}")


@router.callback_query(SetCb.filter(F.action == "tzcustom"))
async def on_tz_custom(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.set_state(SettingsState.timezone)
    await edit_or_send(call, t(lang, "tz_custom_prompt"), custom_tz_kb(lang))
    await call.answer()


@router.message(SettingsState.timezone, F.text)
async def on_tz_typed(message: Message, state: FSMContext, db_user: dict, lang: str) -> None:
    name = tz_from_input(message.text)
    if name is None:
        await message.answer(t(lang, "tz_bad"))
        return
    await user_db.set_timezone(message.from_user.id, name)
    await state.clear()
    await message.answer(t(lang, "tz_changed", tz=tz_title(name, lang)), reply_markup=main_menu_kb(lang))
    await show_settings(message, await _fresh(message.from_user.id, db_user), lang)


# ------------------------------------------------------------------ soatni moslash ("menda 2:37, botda 4:37" muammosi uchun)
@router.callback_query(SetCb.filter(F.action == "clock"))
async def on_clock(call: CallbackQuery, state: FSMContext, db_user: dict, lang: str) -> None:
    tz = get_tz(db_user["timezone"])
    await state.set_state(SettingsState.clock)
    await edit_or_send(
        call, t(lang, "clock_prompt", now=fmt_clock(utcnow(), tz), tz=tz_title(db_user["timezone"], lang)),
        back_to_settings_kb(lang),
    )
    await call.answer()


@router.message(SettingsState.clock, F.text)
async def on_clock_typed(message: Message, state: FSMContext, db_user: dict, lang: str) -> None:
    m = _CLOCK_RE.match(message.text)
    if not m or int(m[1]) > 23 or int(m[2]) > 59:
        await message.answer(t(lang, "clock_bad"))
        return
    now = utcnow()
    tz = get_tz(db_user["timezone"])
    current = utc_offset_minutes(tz, now)
    offset = offset_from_local_clock(int(m[1]), int(m[2]), now, current, (m[3] or "").lower() or None)
    zone = zone_for_offset_minutes(offset) if offset is not None else None
    if zone is None:
        await message.answer(t(lang, "clock_nozone"))
        return
    await state.clear()
    if offset == current:  # soat allaqachon to'g'ri
        await message.answer(
            t(lang, "clock_same", now=fmt_clock(now, tz), tz=tz_title(db_user["timezone"], lang)),
            reply_markup=main_menu_kb(lang),
        )
        return
    await user_db.set_timezone(message.from_user.id, zone)
    await message.answer(
        t(lang, "clock_done", tz=tz_title(zone, lang), now=fmt_clock(now, get_tz(zone))), reply_markup=main_menu_kb(lang)
    )


# ------------------------------------------------------------------ til
@router.callback_query(SetCb.filter(F.action == "lang"))
async def on_lang(call: CallbackQuery, lang: str) -> None:
    await edit_or_send(call, t(lang, "lang_pick"), language_kb(lang))
    await call.answer()


@router.callback_query(SetCb.filter(F.action == "langset"))
async def on_lang_set(call: CallbackQuery, callback_data: SetCb, db_user: dict) -> None:
    code = callback_data.value
    if code not in LANGS:
        await call.answer()
        return
    await user_db.set_language(call.from_user.id, code)
    fresh = await _fresh(call.from_user.id, db_user)
    fresh["language"] = code
    await show_settings(call, fresh, code)
    await send_new(call, t(code, "lang_changed"), main_menu_kb(code))  # menyuni yangi tilda yangilaymiz
    await call.answer()


# ------------------------------------------------------------------ kunlik xulosa
@router.callback_query(SetCb.filter(F.action == "digest"))
async def on_digest(call: CallbackQuery, db_user: dict, lang: str) -> None:
    enabled = not bool(db_user["digest_enabled"])
    await user_db.set_digest(call.from_user.id, enabled)
    await show_settings(call, await _fresh(call.from_user.id, db_user), lang)
    await call.answer(t(lang, "digest_toast_on" if enabled else "digest_toast_off"))


# ------------------------------------------------------------------ ma'lumotlarni o'chirish
@router.callback_query(SetCb.filter(F.action == "wipe"))
async def on_wipe(call: CallbackQuery, lang: str) -> None:
    await edit_or_send(call, t(lang, "wipe_ask"), wipe_confirm_kb(lang))
    await call.answer()


@router.callback_query(SetCb.filter(F.action == "wipeyes"))
async def on_wipe_yes(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await user_db.delete(call.from_user.id)
    await edit_or_send(call, t(lang, "wipe_done"))
    await call.answer()
