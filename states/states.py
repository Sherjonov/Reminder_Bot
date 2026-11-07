"""FSM holatlari (suhbat bosqichlari)."""
from aiogram.fsm.state import State, StatesGroup


class NewReminder(StatesGroup):
    """Yangi eslatma yaratish: tur -> matn -> vaqt -> tasdiqlash."""
    category = State()
    text = State()
    when = State()
    confirm = State()
    edit_text = State()


class EditReminder(StatesGroup):
    """Mavjud eslatmani tahrirlash."""
    text = State()
    when = State()


class TimerState(StatesGroup):
    custom = State()


class SettingsState(StatesGroup):
    timezone = State()
    clock = State()


class ExpenseState(StatesGroup):
    """Xarajatlar bo'limi."""
    adding = State()       # xarajat qo'shish rejimi (har bir xabar — yangi xarid)
    set_total = State()    # umumiy summani o'zgartirish
    topup = State()        # pul qo'shish
    edit_title = State()   # xarid nomini tahrirlash
    edit_price = State()   # xarid narxini tahrirlash
    quick = State()        # erkin matndan topilgan xarajatni tasdiqlash


class BroadcastState(StatesGroup):
    message = State()
    confirm = State()
