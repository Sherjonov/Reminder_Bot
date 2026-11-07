"""Admin: barcha foydalanuvchilarga xabar yuborish (matn, rasm, video — nima bo'lsa)."""
import asyncio
import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from filters import IsCancelText, admins_only
from keyboards.inline.admin import admin_back_kb, broadcast_confirm_kb
from keyboards.inline.callbacks import AdminCb
from services.db_api import users as user_db
from services.flow import edit_or_send
from services.messaging import broadcast
from services.misc.i18n import t
from states import BroadcastState

logger = logging.getLogger(__name__)

router = Router(name="admin_broadcast")
admins_only(router)

_tasks: set[asyncio.Task] = set()  # fon vazifalarini "yo'qolib" qolishdan saqlaymiz


@router.callback_query(AdminCb.filter(F.action == "broadcast"))
async def on_start(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.set_state(BroadcastState.message)
    await edit_or_send(call, t(lang, "admin_bc_prompt"))
    await call.answer()


@router.message(BroadcastState.message, Command("bekor", "cancel"))
@router.message(BroadcastState.message, IsCancelText())
async def on_cancel_text(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    await message.answer(t(lang, "cancelled"))


@router.message(BroadcastState.message)
async def on_message(message: Message, state: FSMContext, lang: str) -> None:
    await state.update_data(src_chat=message.chat.id, src_message=message.message_id)
    await state.set_state(BroadcastState.confirm)
    total = len(await user_db.all_ids())
    await message.copy_to(message.chat.id)  # ko'rib chiqish uchun nusxa
    await message.answer(t(lang, "admin_bc_confirm", n=total), reply_markup=broadcast_confirm_kb(lang))


@router.callback_query(AdminCb.filter(F.action == "bc_no"), BroadcastState.confirm)
async def on_no(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await edit_or_send(call, t(lang, "admin_bc_cancelled"), admin_back_kb(lang))
    await call.answer()


@router.callback_query(AdminCb.filter(F.action == "bc_yes"), BroadcastState.confirm)
async def on_yes(call: CallbackQuery, state: FSMContext, bot: Bot, lang: str) -> None:
    data = await state.get_data()
    await state.clear()
    user_ids = await user_db.all_ids()
    await edit_or_send(call, t(lang, "admin_bc_started", n=len(user_ids)))
    await call.answer()

    task = asyncio.create_task(_run(bot, call.from_user.id, lang, user_ids, data["src_chat"], data["src_message"]))
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)


async def _run(bot: Bot, admin_id: int, lang: str, user_ids: list[int], src_chat: int, src_message: int) -> None:
    try:
        sent, failed = await broadcast(bot, user_ids, src_chat, src_message)
        await bot.send_message(admin_id, t(lang, "admin_bc_report", sent=sent, failed=failed))
    except Exception:  # noqa: BLE001
        logger.exception("Ommaviy xabar yuborishda xatolik")
