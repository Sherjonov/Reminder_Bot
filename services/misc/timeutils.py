"""Vaqt bilan ishlash yordamchilari.

Bazada barcha vaqtlar UTC (timezone'siz DATETIME) ko'rinishida saqlanadi,
foydalanuvchiga ko'rsatishda esa uning vaqt mintaqasiga o'tkaziladi.

`utcnow()` kompyuter soatiga to'g'ridan-to'g'ri ishonmaydi: `services/time_sync.py` Telegram serveri vaqti bilan
solishtirib, kompyuter soati noto'g'ri bo'lsa (masalan, Windows vaqt mintaqasi xato qo'yilgan) tuzatish (offset) beradi.
"""
from __future__ import annotations

import calendar
import re
from datetime import datetime, timedelta, timezone, tzinfo
from functools import lru_cache
from zoneinfo import ZoneInfo

DEFAULT_TZ = "Asia/Tashkent"

# (IANA nomi, (o'zbekcha, ruscha, inglizcha nomi)) — sozlamalarda tez tanlash uchun
TIMEZONES: list[tuple[str, tuple[str, str, str]]] = [
    ("Asia/Tashkent", ("O'zbekiston — Xorazm, Toshkent", "Узбекистан — Хорезм, Ташкент", "Uzbekistan — Khorezm, Tashkent")),
    ("Europe/Moscow", ("Moskva", "Москва", "Moscow")),
    ("Asia/Almaty", ("Olmaota", "Алматы", "Almaty")),
    ("Europe/Istanbul", ("Istanbul", "Стамбул", "Istanbul")),
    ("Asia/Dubai", ("Dubay", "Дубай", "Dubai")),
    ("Asia/Seoul", ("Seul", "Сеул", "Seoul")),
    ("Europe/Berlin", ("Berlin", "Берлин", "Berlin")),
    ("America/New_York", ("Nyu-York", "Нью-Йорк", "New York")),
]
_LANG_INDEX = {"uz": 0, "ru": 1, "en": 2}

# o'zbekistonning barcha viloyatlari bitta vaqt mintaqasida (UTC+5)
_ALIASES = {
    "toshkent": "Asia/Tashkent", "tashkent": "Asia/Tashkent", "ташкент": "Asia/Tashkent",
    "xorazm": "Asia/Tashkent", "khorezm": "Asia/Tashkent", "хорезм": "Asia/Tashkent", "urganch": "Asia/Tashkent",
    "ургенч": "Asia/Tashkent", "uzbekistan": "Asia/Tashkent", "o'zbekiston": "Asia/Tashkent",
    "ozbekiston": "Asia/Tashkent", "узбекистан": "Asia/Tashkent", "samarqand": "Asia/Tashkent",
    "buxoro": "Asia/Tashkent", "andijon": "Asia/Tashkent", "namangan": "Asia/Tashkent", "farg'ona": "Asia/Tashkent",
    "moscow": "Europe/Moscow", "moskva": "Europe/Moscow", "москва": "Europe/Moscow",
    "seoul": "Asia/Seoul", "seul": "Asia/Seoul", "сеул": "Asia/Seoul",
    "istanbul": "Europe/Istanbul", "стамбул": "Europe/Istanbul",
    "dubai": "Asia/Dubai", "dubay": "Asia/Dubai", "дубай": "Asia/Dubai",
    "almaty": "Asia/Almaty", "olmaota": "Asia/Almaty", "алматы": "Asia/Almaty",
    "berlin": "Europe/Berlin", "берлин": "Europe/Berlin",
    "new york": "America/New_York", "nyu-york": "America/New_York", "нью-йорк": "America/New_York",
}

# tzdata o'rnatilmagan bo'lsa ham Toshkent vaqti ishlashi uchun
_FALLBACK = timezone(timedelta(hours=5), "Asia/Tashkent")

# Kompyuter soatiga tuzatish (time_sync.py o'rnatadi)
_CLOCK_OFFSET = timedelta(0)


def set_clock_offset(offset: timedelta) -> None:
    global _CLOCK_OFFSET
    _CLOCK_OFFSET = offset


def get_clock_offset() -> timedelta:
    return _CLOCK_OFFSET


@lru_cache(maxsize=256)
def get_tz(name: str | None) -> tzinfo:
    try:
        return ZoneInfo(name or DEFAULT_TZ)
    except Exception:
        return _FALLBACK


def is_valid_tz(name: str) -> bool:
    if not name or len(name) > 64:
        return False
    try:
        ZoneInfo(name)
        return True
    except Exception:
        return False


def utcnow() -> datetime:
    """Hozirgi UTC vaqt (timezone'siz — bazadagi DATETIME bilan bir xil). Kompyuter soati xatosi tuzatilgan."""
    return datetime.now(timezone.utc).replace(tzinfo=None) + _CLOCK_OFFSET


def to_local(dt_utc: datetime, tz: tzinfo) -> datetime:
    return dt_utc.replace(tzinfo=timezone.utc).astimezone(tz)


def to_utc(dt_local: datetime) -> datetime:
    return dt_local.astimezone(timezone.utc).replace(tzinfo=None)


def add_months(dt: datetime, months: int, anchor_day: int | None = None) -> datetime:
    """Sanani oyga suradi; oyda kun yetmasa oxirgi kunga tushadi (31-yanvar -> 28/29-fevral)."""
    index = dt.month - 1 + months
    year = dt.year + index // 12
    month = index % 12 + 1
    day = min(anchor_day or dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def utc_offset_minutes(tz: tzinfo, now_utc: datetime | None = None) -> int:
    offset = to_local(now_utc or utcnow(), tz).utcoffset() or timedelta(0)
    return int(offset.total_seconds() // 60)


def utc_offset_label(tz: tzinfo, now_utc: datetime | None = None) -> str:
    total = utc_offset_minutes(tz, now_utc)
    sign = "+" if total >= 0 else "-"
    hours, minutes = divmod(abs(total), 60)
    return f"UTC{sign}{hours}" + (f":{minutes:02d}" if minutes else "")


def tz_title(name: str, lang: str = "uz") -> str:
    if name == "UTC" or name.startswith("Etc/GMT"):
        return utc_offset_label(get_tz(name))
    names = dict(TIMEZONES).get(name)
    base = names[_LANG_INDEX.get(lang, 0)] if names else name.split("/")[-1].replace("_", " ")
    return f"{base} ({utc_offset_label(get_tz(name))})"


_OFFSET_RE = re.compile(r"^(?:utc|gmt)?\s*([+-])\s*(\d{1,2})$")


def tz_from_input(text: str) -> str | None:
    """Foydalanuvchi yozgan matndan IANA vaqt mintaqasini topadi: '+5', 'UTC+3', 'Asia/Tokyo', 'Moskva', 'Xorazm'."""
    raw = (text or "").strip()
    if not raw:
        return None
    m = _OFFSET_RE.match(raw.lower())
    if m:
        sign, hours = m.group(1), int(m.group(2))
        if hours > 14:
            return None
        if hours == 0:
            return "UTC"
        # Etc/GMT belgisi teskari: UTC+5 -> Etc/GMT-5
        return f"Etc/GMT{'-' if sign == '+' else '+'}{hours}"

    low = raw.lower().replace("’", "'").replace("ʻ", "'")
    if low in _ALIASES:
        return _ALIASES[low]
    for iana, names in TIMEZONES:
        if low in (n.lower() for n in names):
            return iana

    candidate = raw.replace(" ", "_")
    for name in (raw, candidate, candidate.title()):
        if is_valid_tz(name):
            return name
    return None


# ---------------------------------------------------------------- soatni moslash (kalibrovka)
_SPECIAL_OFFSETS = {
    330: "Asia/Kolkata", 345: "Asia/Kathmandu", 270: "Asia/Kabul", 210: "Asia/Tehran",
    570: "Australia/Darwin", -210: "America/St_Johns",
}


def zone_for_offset_minutes(total: int) -> str | None:
    """UTC dan farq (daqiqada) bo'yicha mos vaqt mintaqasi nomi."""
    if total == 300:
        return "Asia/Tashkent"
    if total in _SPECIAL_OFFSETS:
        return _SPECIAL_OFFSETS[total]
    if total % 60 == 0:
        hours = total // 60
        if hours == 0:
            return "UTC"
        if -12 <= hours <= 14:
            return f"Etc/GMT{'-' if hours > 0 else '+'}{abs(hours)}"
    return None


def offset_from_local_clock(
    hour: int, minute: int, now_utc: datetime, current_offset: int, ampm: str | None = None
) -> int | None:
    """Foydalanuvchi aytgan "hozirgi soat" bo'yicha UTC dan farqni (daqiqada, 15 ga yaxlitlab) topadi.

    AM/PM noaniq bo'lsa (masalan "2:37") ikkala variant tekshiriladi va hozirgi sozlamaga yaqini tanlanadi.
    """
    utc_min = now_utc.hour * 60 + now_utc.minute
    if ampm == "pm":
        typed = [((hour % 12) + 12) * 60 + minute]
    elif ampm == "am":
        typed = [(hour % 12) * 60 + minute]
    elif 1 <= hour <= 12:
        typed = [(hour % 12) * 60 + minute, (hour % 12 + 12) * 60 + minute]
    else:
        typed = [(hour % 24) * 60 + minute]

    best: tuple[tuple[int, int], int] | None = None
    for value in typed:
        for offset in range(-12 * 60, 14 * 60 + 1, 15):
            delta = ((value - (utc_min + offset) + 720) % 1440) - 720
            if abs(delta) <= 7:
                score = (abs(offset - current_offset), abs(delta))
                if best is None or score < best[0]:
                    best = (score, offset)
    return None if best is None else best[1]
