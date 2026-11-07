"""Ko'p tillilik: o'zbekcha (uz), ruscha (ru), inglizcha (en).

Matnlar `services/misc/locales/` da; `t(lang, "kalit", **qiymatlar)` kerakli tildagi matnni qaytaradi.
"""
from __future__ import annotations

import logging
import re

from .locales import MESSAGES

logger = logging.getLogger(__name__)

LANGS = ("uz", "ru", "en")
DEFAULT_LANG = "uz"
LANG_NAMES = {"uz": "O'zbekcha", "ru": "Русский", "en": "English"}
_INDEX = {"uz": 0, "ru": 1, "en": 2}
_NOISE = re.compile(r"[^\w' ]+", re.UNICODE)


def norm_label(text: str) -> str:
    """Emoji va belgilarsiz, kichik harfli ko'rinish: '➕ Yangi eslatma' -> 'yangi eslatma'."""
    text = text.lower().replace("\u2019", "'").replace("\u02bb", "'")
    return " ".join(_NOISE.sub(" ", text).split())


def lang_from_telegram(code: str | None) -> str:
    """Telegram ilovasidagi til kodidan boshlang'ich tilni tanlaydi (o'zbek bozori uchun standart — uz)."""
    code = (code or "").lower()
    if code.startswith("ru"):
        return "ru"
    if code.startswith("en"):
        return "en"
    return DEFAULT_LANG


def t(lang: str, key: str, **kwargs) -> str:
    entry = MESSAGES.get(key)
    if entry is None:
        logger.error("Tarjima kaliti topilmadi: %s", key)
        return key
    text = entry[_INDEX.get(lang, 0)]
    return text.format(**kwargs) if kwargs else text


def all_labels(key: str) -> set[str]:
    """Bir tugmaning barcha tillardagi (normalizatsiya qilingan) matnlari."""
    return {norm_label(text) for text in MESSAGES[key]}


_LABEL_LANG: dict[str, str] | None = None


def label_language(text: str) -> str | None:
    """Matn menyu tugmasining aniq nusxasi bo'lsa — shu tugma tilini qaytaradi."""
    global _LABEL_LANG
    if _LABEL_LANG is None:
        mapping: dict[str, set[str]] = {}
        for key, entry in MESSAGES.items():
            if key.startswith("btn_"):
                for lang, label in zip(LANGS, entry):
                    mapping.setdefault(norm_label(label), set()).add(lang)
        _LABEL_LANG = {label: next(iter(langs)) for label, langs in mapping.items() if len(langs) == 1}
    return _LABEL_LANG.get(norm_label(text))
