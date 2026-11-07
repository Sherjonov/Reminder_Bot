"""Buyruqlar va asosiy menyu tugmalari (uz / ru / en).

Bu router boshqa FSM routerlardan OLDIN turadi: foydalanuvchi suhbat o'rtasida menyuni bossa,
joriy jarayon bekor bo'lib, tanlangan bo'lim ochiladi.
"""
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from filters import ButtonText, IsCancelText, private_only
from keyboards.default import main_menu_kb
from services.misc.i18n import t

from . import expenses, my_reminders, new_reminder, preferences, start, timer

router = Router(name="user_menu")
private_only(router)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db_user: dict, lang: str) -> None:
    await state.clear()
    await start.show_start(message, db_user, lang)


@router.message(Command("yordam", "help"))
@router.message(ButtonText("btn_help"))
async def cmd_help(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    await message.answer(t(lang, "help"), reply_markup=main_menu_kb(lang))


@router.message(Command("bekor", "cancel"))
@router.message(IsCancelText())
async def cmd_cancel(message: Message, state: FSMContext, lang: str) -> None:
    current = await state.get_state()
    await state.clear()
    await message.answer(t(lang, "cancelled" if current else "nothing_to_cancel"), reply_markup=main_menu_kb(lang))


@router.message(Command("yangi", "new"))
@router.message(ButtonText("btn_new"))
async def cmd_new(message: Message, state: FSMContext, lang: str) -> None:
    await new_reminder.begin(message, state, lang)


@router.message(Command("taymer", "timer"))
@router.message(ButtonText("btn_timer"))
async def cmd_timer(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    await timer.show_timer(message, lang)


@router.message(Command("eslatmalar", "list"))
@router.message(ButtonText("btn_list"))
async def cmd_list(message: Message, state: FSMContext, db_user: dict, lang: str) -> None:
    await state.clear()
    await my_reminders.show_list(message, db_user, lang)


@router.message(Command("bugun", "today"))
@router.message(ButtonText("btn_today"))
async def cmd_today(message: Message, state: FSMContext, db_user: dict, lang: str) -> None:
    await state.clear()
    await my_reminders.show_list(message, db_user, lang, scope="t")


@router.message(Command("xarajatlar", "expenses", "xarajat"))
@router.message(ButtonText("btn_expenses"))
async def cmd_expenses(message: Message, state: FSMContext, db_user: dict, lang: str) -> None:
    await state.clear()
    await expenses.show_home(message, db_user, lang)


@router.message(Command("sozlamalar", "settings"))
@router.message(ButtonText("btn_settings"))
async def cmd_settings(message: Message, state: FSMContext, db_user: dict, lang: str) -> None:
    await state.clear()
    await preferences.show_settings(message, db_user, lang)


@router.message(Command("vaqt", "time", "soat"))
async def cmd_time(message: Message, state: FSMContext, db_user: dict, lang: str) -> None:
    await state.clear()
    await preferences.show_time(message, db_user, lang)
