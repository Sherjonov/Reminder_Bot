"""Matnga asoslangan filtrlar: menyu tugmalari (barcha tillarda) va "bekor qilish" so'zlari."""
from aiogram.filters import BaseFilter
from aiogram.types import Message

from services.misc.i18n import all_labels, norm_label

normalize_button = norm_label


class ButtonText(BaseFilter):
    """Menyu tugmasi matniga mos keladimi — uz / ru / en dan istalgani (emojisiz yozilsa ham)."""

    def __init__(self, *keys: str) -> None:
        self.labels: set[str] = set()
        for key in keys:
            self.labels |= all_labels(key)

    async def __call__(self, message: Message) -> bool:
        return bool(message.text) and norm_label(message.text) in self.labels


class IsCancelText(BaseFilter):
    WORDS = {"bekor", "bekor qilish", "cancel", "отмена", "отменить"}

    async def __call__(self, message: Message) -> bool:
        return bool(message.text) and norm_label(message.text) in self.WORDS
