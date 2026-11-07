"""Inline tugmalar uchun callback ma'lumotlari (har biri 64 baytdan oshmasligi kerak)."""
from aiogram.filters.callback_data import CallbackData


class CatCb(CallbackData, prefix="cat"):
    key: str


class WhenCb(CallbackData, prefix="when"):
    key: str


class RepCb(CallbackData, prefix="rep"):
    kind: str           # none | daily | weekly | monthly | weekdays | yearly | interval | back
    value: int = 0      # interval uchun daqiqalar (0 — menyuni ochish)


class ConfirmCb(CallbackData, prefix="cf"):
    action: str         # save | time | text | cancel


class RemCb(CallbackData, prefix="rem"):
    action: str         # open | page | etext | etime | del | delyes | new | noop
    id: int = 0
    page: int = 0
    scope: str = "a"    # a — hammasi, t — bugun


class FireCb(CallbackData, prefix="fire"):
    action: str         # done | snooze | again | ok
    id: int
    value: int = 0


class TimerCb(CallbackData, prefix="tmr"):
    action: str         # start | custom | cancel | menu
    minutes: int = 0
    id: int = 0


class SetCb(CallbackData, prefix="set"):
    action: str         # tz | tzset | tzcustom | digest | wipe | wipeyes | back | lang | langset | clock
    value: str = ""


class AdminCb(CallbackData, prefix="adm"):
    action: str         # stats | backup | broadcast | bc_yes | bc_no | home


class GroupCb(CallbackData, prefix="grp"):
    action: str         # del
    id: int = 0


class FinCb(CallbackData, prefix="fin"):
    action: str         # home | add | done | undo | list | open | etitle | eprice | del | delyes | set | topup | log | qyes | qno | noop
    id: int = 0
    page: int = 0
