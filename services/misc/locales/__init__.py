"""Barcha tarjimalar: kalit -> (o'zbekcha, ruscha, inglizcha)."""
from . import common, finance, reminders, settings

MESSAGES: dict[str, tuple[str, str, str]] = {}
for _module in (common, reminders, settings, finance):
    _duplicates = MESSAGES.keys() & _module.MESSAGES.keys()
    assert not _duplicates, f"Takroriy tarjima kalitlari: {_duplicates}"
    MESSAGES.update(_module.MESSAGES)

__all__ = ["MESSAGES"]
