"""Guruhlarda eslatma: /eslat <vaqt> <matn>, /eslatmalar — uz / ru / en."""
from __future__ import annotations

import logging
from datetime import timedelta

from aiogram import Bot, F, Router
from aiogram.filters import JOIN_TRANSITION, ChatMemberUpdatedFilter, Command, CommandObject
from aiogram.types import CallbackQuery, ChatMemberUpdated, InlineKeyboardMarkup, Message

from config import settings
from filters import groups_only
from keyboards.inline.admin import group_list_kb
from keyboards.inline.callbacks import GroupCb
from services.db_api import reminders as rem_db
from services.db_api import users as user_db
from services.flow import edit_or_send
from services.misc.constants import CATEGORY_EMOJI, MAX_ACTIVE_PER_CHAT, MAX_TEXT_LEN, MIN_LEAD_SECONDS
from services.misc.formatting import esc, fmt_in, fmt_when, short
from services.misc.i18n import lang_from_telegram, t
from services.misc.langdetect import detect_language
from services.misc.time_parser import guess_category, parse_when
from services.misc.timeutils import get_tz, utcnow

logger = logging.getLogger(__name__)

router = Router(name="group_reminders")
groups_only(router)


def _lang(user, text: str = "") -> str:
    return detect_language(text) or lang_from_telegram(user.language_code if user else None)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def on_bot_added(event: ChatMemberUpdated, bot: Bot) -> None:
    await bot.send_message(event.chat.id, t(lang_from_telegram(event.from_user.language_code), "g_help"))


@router.message(Command("start", "yordam", "help"))
async def group_help(message: Message) -> None:
    await message.answer(t(_lang(message.from_user), "g_help"))


@router.message(Command("eslat", "remind"))
async def create_reminder(message: Message, command: CommandObject) -> None:
    user = message.from_user
    lang = _lang(user, command.args or "")
    if user is None or user.is_bot or message.sender_chat is not None:
        await message.answer(t(lang, "g_anon"))
        return
    if not command.args:
        await message.answer(t(lang, "g_help"))
        return

    db_user = await user_db.touch(user)
    lang = detect_language(command.args) or db_user.get("language") or lang
    result = parse_when(command.args, get_tz(db_user["timezone"]), loose=False)
    if result is None or len(result.remainder) < 2:
        await message.answer(t(lang, "g_bad"))
        return
    if len(result.remainder) > MAX_TEXT_LEN:
        await message.answer(t(lang, "g_long", max=MAX_TEXT_LEN))
        return
    if result.dt_utc <= utcnow() + timedelta(seconds=MIN_LEAD_SECONDS):
        await message.answer(t(lang, "g_past"))
        return
    if await rem_db.count_chat(message.chat.id) >= MAX_ACTIVE_PER_CHAT:
        await message.answer(t(lang, "g_limit", max=MAX_ACTIVE_PER_CHAT))
        return

    rem_id = await rem_db.create(
        user_id=user.id, chat_id=message.chat.id, text=result.remainder, remind_at=result.dt_utc,
        category=guess_category(result.remainder), tz=db_user["timezone"],
    )
    tz = get_tz(db_user["timezone"])
    await message.answer(t(
        lang, "g_saved", id=rem_id, text=esc(result.remainder), when=fmt_when(result.dt_utc, tz, lang),
        in_=fmt_in((result.dt_utc - utcnow()).total_seconds(), lang),
    ))


async def render_list(chat_id: int, tz, lang: str) -> tuple[str, InlineKeyboardMarkup | None]:
    items = await rem_db.list_chat(chat_id, 10)
    if not items:
        return t(lang, "g_empty"), None
    now = utcnow()
    blocks = [t(lang, "g_list_title", n=len(items))]
    for rem in items:
        emoji = CATEGORY_EMOJI.get(rem["category"], "🔔")
        blocks.append(
            f"<b>#{rem['id']}</b> {emoji} {esc(short(rem['text'], 50))}\n"
            f"      🕒 {fmt_when(rem['remind_at'], tz, lang, now, weekday=False)} · 👤 {esc(short(rem['full_name'], 20))}"
        )
    blocks.append(t(lang, "g_list_hint"))
    return "\n\n".join(blocks), group_list_kb(items)


@router.message(Command("eslatmalar", "reminders"))
async def list_reminders(message: Message) -> None:
    tz, lang = get_tz(settings.default_tz), _lang(message.from_user)
    if message.from_user and not message.from_user.is_bot:
        db_user = await user_db.touch(message.from_user)
        tz, lang = get_tz(db_user["timezone"]), db_user.get("language") or lang
    text, markup = await render_list(message.chat.id, tz, lang)
    await message.answer(text, reply_markup=markup)


@router.callback_query(GroupCb.filter(F.action == "del"))
async def delete_reminder(call: CallbackQuery, callback_data: GroupCb, bot: Bot) -> None:
    lang = lang_from_telegram(call.from_user.language_code)
    rem = await rem_db.get(callback_data.id)
    chat = call.message.chat if call.message else None
    if not rem or chat is None or rem["chat_id"] != chat.id or rem["status"] != "active":
        await call.answer(t(lang, "rem_nf_short"), show_alert=True)
        return

    allowed = rem["user_id"] == call.from_user.id or call.from_user.id in settings.admins
    if not allowed:
        member = await bot.get_chat_member(chat.id, call.from_user.id)
        allowed = member.status in ("creator", "administrator")
    if not allowed:
        await call.answer(t(lang, "g_forbidden"), show_alert=True)
        return

    await rem_db.delete(rem["id"])
    await call.answer(t(lang, "deleted_toast"))
    db_user = await user_db.touch(call.from_user)
    text, markup = await render_list(chat.id, get_tz(db_user["timezone"]), db_user.get("language") or lang)
    await edit_or_send(call, text, markup)
