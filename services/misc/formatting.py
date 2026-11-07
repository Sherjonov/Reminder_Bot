"""Matnlarni chiroyli ko'rsatish: sana, davomiylik, eslatma kartochkasi (uz / ru / en)."""
from __future__ import annotations

import html
from datetime import datetime, tzinfo

from .constants import CATEGORY_EMOJI
from .i18n import t
from .timeutils import to_local, utcnow

WEEKDAYS = {
    "uz": ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"],
    "ru": ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"],
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
}
MONTHS = {
    "uz": ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr"],
    "ru": ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"],
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
           "November", "December"],
}
_UNITS = {
    "uz": {"d": ("kun",), "h": ("soat",), "m": ("daqiqa",)},
    "ru": {"d": ("день", "дня", "дней"), "h": ("час", "часа", "часов"), "m": ("минута", "минуты", "минут")},
    "en": {"d": ("day", "days"), "h": ("hour", "hours"), "m": ("minute", "minutes")},
}


def esc(text: object) -> str:
    """Foydalanuvchi matnini HTML uchun xavfsiz qiladi."""
    return html.escape(str(text), quote=False)


def short(text: str, limit: int = 40) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _plural(lang: str, n: int, forms: tuple[str, ...]) -> str:
    if lang == "ru":
        n10, n100 = n % 10, n % 100
        if n10 == 1 and n100 != 11:
            return forms[0]
        if 2 <= n10 <= 4 and not 12 <= n100 <= 14:
            return forms[1]
        return forms[2]
    if lang == "en":
        return forms[0] if n == 1 else forms[1]
    return forms[0]


def fmt_clock(dt_utc: datetime, tz: tzinfo) -> str:
    return to_local(dt_utc, tz).strftime("%H:%M")


def fmt_when(dt_utc: datetime, tz: tzinfo, lang: str = "uz", now_utc: datetime | None = None, weekday: bool = True) -> str:
    """'Bugun, 18:30' / 'Ertaga, 09:00' / '25-dekabr, Juma, 14:00' (tilga qarab)."""
    lang = lang if lang in WEEKDAYS else "uz"
    now_utc = now_utc or utcnow()
    local = to_local(dt_utc, tz)
    today = to_local(now_utc, tz).date()
    diff = (local.date() - today).days
    if diff == 0:
        label = t(lang, "d_today")
    elif diff == 1:
        label = t(lang, "d_tomorrow")
    else:
        month = MONTHS[lang][local.month - 1]
        if lang == "en":
            label = f"{month} {local.day}"
        elif lang == "ru":
            label = f"{local.day} {month}"
        else:
            label = f"{local.day}-{month}"
        if local.year != today.year:
            label += f" {local.year}"
        if weekday:
            label += f", {WEEKDAYS[lang][local.weekday()]}"
    return f"{label}, {local.strftime('%H:%M')}"


def fmt_minutes(minutes: int, lang: str = "uz", max_parts: int = 3) -> str:
    """90 -> '1 soat 30 daqiqa' / '1 час 30 минут' / '1 hour 30 minutes'."""
    lang = lang if lang in _UNITS else "uz"
    minutes = max(int(minutes), 0)
    days, rest = divmod(minutes, 1440)
    hours, mins = divmod(rest, 60)
    units = _UNITS[lang]
    parts: list[str] = []
    if days:
        parts.append(f"{days} {_plural(lang, days, units['d'])}")
    if hours:
        parts.append(f"{hours} {_plural(lang, hours, units['h'])}")
    if mins or not parts:
        parts.append(f"{mins} {_plural(lang, mins, units['m'])}")
    return " ".join(parts[:max_parts])


def fmt_in(seconds: float, lang: str = "uz") -> str:
    """'14 soat 20 daqiqadan keyin' / 'через 14 часов 20 минут' / 'in 14 hours 20 minutes'."""
    minutes = int((max(seconds, 0) + 30) // 60)  # eng yaqin daqiqaga yaxlitlaymiz (29:59 -> 30 daqiqa)
    if minutes < 1:
        return t(lang, "in_lt_min")
    return t(lang, "in_fmt", dur=fmt_minutes(minutes, lang, 2))


def repeat_label(repeat_type: str | None, repeat_value: int | None, lang: str = "uz") -> str:
    if repeat_type == "interval" and repeat_value:
        value = int(repeat_value)
        if value % 60 == 0:
            return t(lang, "rep_interval_h", n=value // 60)
        return t(lang, "rep_interval_m", n=value)
    if repeat_type in ("daily", "weekly", "monthly", "yearly", "weekdays"):
        return t(lang, f"rep_{repeat_type}")
    return t(lang, "rep_none")


def category_name(key: str, lang: str = "uz") -> str:
    return t(lang, f"cat_{key if key in CATEGORY_EMOJI else 'other'}")


def category_label(key: str, lang: str = "uz") -> str:
    return f"{CATEGORY_EMOJI.get(key, CATEGORY_EMOJI['other'])} {category_name(key, lang)}"


def reminder_card(rem: dict, tz: tzinfo, lang: str = "uz", now_utc: datetime | None = None) -> str:
    emoji = CATEGORY_EMOJI.get(rem["category"], CATEGORY_EMOJI["other"])
    lines = [f"{emoji} <b>{category_name(rem['category'], lang)}</b>"]
    when = fmt_when(rem["remind_at"], tz, lang, now_utc)
    if rem["category"] == "timer":
        duration = fmt_minutes(rem["duration_min"], lang) if rem.get("duration_min") else esc(rem["text"])
        lines.append(t(lang, "card_timer_dur", dur=duration))
        lines += ["", t(lang, "card_timer_end", when=when)]
    else:
        lines.append(esc(rem["text"]))
        lines += ["", t(lang, "card_when", when=when)]
        if rem["repeat_type"] != "none":
            lines.append(t(lang, "card_repeat", repeat=repeat_label(rem["repeat_type"], rem["repeat_value"], lang)))
    return "\n".join(lines)


def list_item_line(index: int, rem: dict, tz: tzinfo, lang: str = "uz", now_utc: datetime | None = None) -> str:
    emoji = CATEGORY_EMOJI.get(rem["category"], CATEGORY_EMOJI["other"])
    if rem["category"] == "timer":
        duration = fmt_minutes(rem["duration_min"], lang) if rem.get("duration_min") else esc(rem["text"])
        return t(lang, "item_timer", i=index, emoji=emoji, dur=duration, clock=fmt_clock(rem["remind_at"], tz))
    return t(
        lang, "item_line", i=index, emoji=emoji, text=esc(short(rem["text"], 45)),
        when=fmt_when(rem["remind_at"], tz, lang, now_utc, weekday=False),
        rep=" 🔁" if rem["repeat_type"] != "none" else "",
    )


def fired_text(rem: dict, tz: tzinfo, lang: str = "uz", late_seconds: float = 0.0, mention: str | None = None) -> str:
    """Eslatma vaqti kelganda foydalanuvchiga boradigan xabar."""
    if rem["category"] == "timer":
        minutes = rem.get("duration_min") or 0
        text = t(lang, "fired_timer")
        return text + (f"\n\n{t(lang, 'fired_timer_body', dur=fmt_minutes(minutes, lang))}" if minutes else "")

    emoji = CATEGORY_EMOJI.get(rem["category"], CATEGORY_EMOJI["other"])
    lines = [t(lang, "fired_title"), "", f"{emoji} <b>{category_name(rem['category'], lang)}</b>", esc(rem["text"]), ""]
    clock = fmt_clock(rem["remind_at"], tz)
    if rem["repeat_type"] != "none":
        lines.append(f"🕒 {clock} · 🔁 {repeat_label(rem['repeat_type'], rem['repeat_value'], lang)}")
    else:
        lines.append(f"🕒 {clock}")
    if late_seconds > 120:
        lines.append(t(lang, "fired_late", dur=fmt_minutes(int(late_seconds // 60), lang, 2)))
    if mention:
        lines.append(f"👤 {mention}")
    return "\n".join(lines)


def digest_text(items: list[dict], tz: tzinfo, lang: str = "uz") -> str:
    lines = [t(lang, "digest_title"), t(lang, "digest_header", n=len(items)), ""]
    for rem in items:
        emoji = CATEGORY_EMOJI.get(rem["category"], CATEGORY_EMOJI["other"])
        lines.append(f"• <b>{fmt_clock(rem['remind_at'], tz)}</b> — {emoji} {esc(short(rem['text'], 60))}")
    lines += ["", t(lang, "digest_footer")]
    return "\n".join(lines)
