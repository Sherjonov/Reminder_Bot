"""Admin paneli: statistika va zaxira (backup)."""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from filters import admins_only
from keyboards.inline.admin import admin_back_kb, admin_kb
from keyboards.inline.callbacks import AdminCb
from services.backup import send_backup
from services.db_api import db
from services.db_api import finance as fin_db
from services.db_api import reminders as rem_db
from services.flow import edit_or_send
from services.misc.i18n import t

router = Router(name="admin_panel")
admins_only(router)


def stats_text(stats: dict, fin_stats: dict, lang: str) -> str:
    by_status = stats["by_status"]
    return t(
        lang, "admin_stats",
        users_total=stats["users_total"], active7=stats["users_active7"], blocked=stats["users_blocked"],
        digest=stats["users_digest"], active=by_status.get("active", 0), sent=by_status.get("sent", 0),
        done=by_status.get("done", 0), failed=by_status.get("failed", 0), created=stats["created_24h"],
        next=stats["next_24h"], wallets=fin_stats["wallets"], expenses=fin_stats["expenses"],
    )


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    await message.answer(t(lang, "admin_panel"), reply_markup=admin_kb(lang))


@router.callback_query(AdminCb.filter(F.action == "home"))
async def on_home(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await edit_or_send(call, t(lang, "admin_panel"), admin_kb(lang))
    await call.answer()


@router.callback_query(AdminCb.filter(F.action == "stats"))
async def on_stats(call: CallbackQuery, lang: str) -> None:
    text = stats_text(await rem_db.stats(), await fin_db.stats(db), lang)
    await edit_or_send(call, text, admin_back_kb(lang))
    await call.answer()


@router.callback_query(AdminCb.filter(F.action == "backup"))
async def on_backup(call: CallbackQuery, lang: str) -> None:
    await call.answer(t(lang, "admin_backup_wait"))
    await send_backup(call.bot, [call.from_user.id])
