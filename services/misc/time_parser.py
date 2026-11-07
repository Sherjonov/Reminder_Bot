"""Tabiiy tildagi vaqt iboralarini tushunish — o'zbekcha, ruscha va inglizcha.

Misollar:
    uz:  "bugun 18:30"   "ertaga soat 9 da"   "30 daqiqadan keyin"   "dushanba 10:00"   "15 mart kechqurun 7 da"
    ru:  "сегодня в 18:30"   "завтра в 9 утра"   "через 30 минут"   "в понедельник в 10:00"   "15 марта в 7 вечера"
    en:  "today 18:30"   "tomorrow at 9am"   "in 30 minutes"   "monday 10:00"   "March 15 at 7 pm"
    umumiy: "25.12 14:00"   "25.12.2026 09:00"

Eslatma: nuqta bilan yozilgan "10.12" — sana (10-dekabr) deb olinadi. Soatni ikki nuqta bilan yozing: "10:12".
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, tzinfo

from .timeutils import add_months, to_local, to_utc, utcnow

_APOS = str.maketrans(
    {"\u2018": "'", "\u2019": "'", "\u02bb": "'", "\u02bc": "'", "`": "'", "\u00b4": "'", "\u2032": "'"}
)

# ---------------------------------------------------------------- lug'atlar
_WEEKDAY_PREFIX = (
    ("dushanba", 0), ("seshanba", 1), ("chorshanba", 2), ("payshanba", 3), ("yakshanba", 6), ("juma", 4), ("shanba", 5),
    ("monday", 0), ("tuesday", 1), ("wednesday", 2), ("thursday", 3), ("friday", 4), ("saturday", 5), ("sunday", 6),
    ("понедел", 0), ("вторн", 1), ("сред", 2), ("четв", 3), ("пятн", 4), ("субб", 5), ("воскр", 6),
)
_MONTH_PREFIX = (
    ("yanvar", 1), ("fevral", 2), ("mart", 3), ("aprel", 4), ("may", 5), ("iyun", 6), ("iyul", 7), ("avgust", 8),
    ("sentabr", 9), ("sentyabr", 9), ("oktabr", 10), ("oktyabr", 10), ("noyabr", 11), ("dekabr", 12),
    ("jan", 1), ("feb", 2), ("mar", 3), ("apr", 4), ("jun", 6), ("jul", 7), ("aug", 8), ("sep", 9),
    ("oct", 10), ("nov", 11), ("dec", 12),
    ("январ", 1), ("феврал", 2), ("март", 3), ("апрел", 4), ("ма", 5), ("июн", 6), ("июл", 7), ("август", 8),
    ("сентябр", 9), ("октябр", 10), ("ноябр", 11), ("декабр", 12),
)
_UNIT_VALUES = {
    "bir": 1, "ikki": 2, "uch": 3, "to'rt": 4, "besh": 5, "olti": 6, "yetti": 7, "sakkiz": 8, "to'qqiz": 9,
    "один": 1, "одну": 1, "два": 2, "две": 2, "три": 3, "четыре": 4, "пять": 5, "шесть": 6, "семь": 7,
    "восемь": 8, "девять": 9,
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
}
_TENS_VALUES = {
    "o'n": 10, "yigirma": 20, "o'ttiz": 30, "qirq": 40, "ellik": 50, "oltmish": 60,
    "десять": 10, "двадцать": 20, "тридцать": 30, "сорок": 40, "пятьдесят": 50,
    "ten": 10, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
}
_TEEN_VALUES = {"пятнадцать": 15, "двенадцать": 12, "fifteen": 15, "twelve": 12}


def _alt(words) -> str:
    return "|".join(sorted(words, key=len, reverse=True))


_NUM_WORD = (
    rf"(?:(?:{_alt(_TENS_VALUES)})(?:\s+(?:{_alt(_UNIT_VALUES)}))?"
    rf"|(?:bir|ikki|uch)\s+yarim|yarim|{_alt(_TEEN_VALUES)}|{_alt(_UNIT_VALUES)})"
)
_UNIT = (
    r"(?:daqiqa|daqiq|daq|minutes?|minut|mins?|минут\w*|мин(?!\w)\.?|"
    r"soat|hours?|hrs?|час\w*|kun|days?|дн\w*|ден\w*|hafta|weeks?|недел\w*|oy|months?|месяц\w*)"
)
_MONTH_ALT = (
    r"yanvar|fevral|mart|aprel|may|iyun|iyul|avgust|sentabr|sentyabr|oktabr|oktyabr|noyabr|dekabr|"
    r"january|february|march|april|june|july|august|september|october|november|december|"
    r"jan|feb|mar|apr|jun|jul|aug|sept|sep|oct|nov|dec|"
    r"январ\w*|феврал\w*|март\w*|апрел\w*|ма[яй]|июн\w*|июл\w*|август\w*|сентябр\w*|октябр\w*|ноябр\w*|декабр\w*"
)
_EN_MONTH_ALT = (
    r"january|february|march|april|may|june|july|august|september|october|november|december|"
    r"jan|feb|mar|apr|jun|jul|aug|sept|sep|oct|nov|dec"
)

# ---------------------------------------------------------------- regexlar
# "30 daqiqadan keyin", "через 30 минут", "in 2 hours", "1 soat 30 daqiqa", "yarim soatdan so'ng"
_REL_RE = re.compile(
    r"(?:(?P<pre>через|in)\s+)?(?<!\bв )(?<![\w:.])"
    rf"(?P<num>\d{{1,3}}(?:[.,]\d+)?|{_NUM_WORD})\s*(?P<unit>{_UNIT})\w*"
    r"(?P<after>\s+(?:keyinroq|keyin|so'ng|o'tib|o'tgach|later|спустя))?"
)
_SPECIAL_REL_RE = re.compile(
    r"\b(?:через|in)\s+(?:(?P<half>полчаса|half an hour|half hour)|(?P<hour>час|an hour|one hour)|"
    r"(?P<minute>минуту|a minute|one minute))(?!\w)"
)

_SFX = r"(?:\s*(?:da|dan|ga|час\w*)\b)?"
_COLON_RE = re.compile(
    r"(?:\b(?:soat|в|at)\s*)?(?<![\d:.])(?P<h>\d{1,2})\s*:\s*(?P<m>\d{2})(?![\d:])(?:\s*(?P<ap>am|pm)\b)?" + _SFX
)
_AT_RE = re.compile(
    r"\b(?P<kw>soat|в|at)\s*(?P<h>\d{1,2})(?![\d:]|\.\d)(?:\s*(?P<sfx>da|dan|ga|час\w*|o'clock)(?!\w))?"
)
_AMPM_RE = re.compile(r"(?:\bat\s*)?(?<![\d:.])(?P<h>\d{1,2})\s*(?P<ap>am|pm)\b" + _SFX)
_DOTTIME_RE = re.compile(
    r"(?:\b(?:soat|в|at)\s*)?(?<![\d:.])(?P<h>\d{1,2})\.(?P<m>\d{2})(?![\d:]|\.\d)" + _SFX
)
_BARE_RE = re.compile(r"(?<![\d:./\-])(?P<h>\d{1,2})\s*(?:da|ga)\b")

_ISO_RE = re.compile(r"(?<!\d)(?P<y>\d{4})-(?P<m>\d{1,2})-(?P<d>\d{1,2})(?!\d)")
_NUMDATE_RE = re.compile(
    r"(?<![\d:.\-/])(?P<d>\d{1,2})(?P<sep>[./-])(?P<m>\d{1,2})(?:(?P=sep)(?P<y>\d{4}|\d{2}))?(?![\d:])"
    r"(?:\s*(?:kuni|da|ga)\b)?"
)
_TEXTDATE_RE = re.compile(
    rf"(?<![\d:.])(?P<d>\d{{1,2}})(?:st|nd|rd|th)?\s*-?\s*(?:of\s+)?(?P<mon>{_MONTH_ALT})\w*"
    r"(?:\s+(?P<y>\d{4})(?!\d))?(?:\s+kuni)?"
)
_ENDATE_RE = re.compile(
    rf"\b(?P<mon>{_EN_MONTH_ALT})\.?\s+(?P<d>\d{{1,2}})(?!\d)(?:st|nd|rd|th)?(?:,?\s+(?P<y>\d{{4}})(?!\d))?"
)
_DAYWORD_RE = re.compile(
    r"\b(?P<w>bugun|ertadan\s+keyin|ertaga|indinga|indin|сегодня|послезавтра|завтра|"
    r"day\s+after\s+tomorrow|today|tomorrow)\w*"
)
_WEEKDAY_RE = re.compile(
    r"\b(?P<wd>dushanba|seshanba|chorshanba|payshanba|yakshanba|juma|shanba|"
    r"monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
    r"понедельник\w*|вторник\w*|сред[ауыео]\w*|четверг\w*|пятниц\w*|суббот\w*|воскресень\w*)\w*(?:\s+kuni)?"
)
_DAYPART_RE = re.compile(
    r"\b(?P<p>tushdan\s+keyin|tushlikda|tushda|kunduzi|tunda|tongda|ertalab\w*|kechqurun\w*|kechki\w*|"
    r"oqshom\w*|kechasi\w*|после\s+обеда|в\s+обед|утр\w*|днем|днём|дня|вечер\w*|ноч\w*|"
    r"morning|noon|afternoon|evening|tonight|night)(?!\w)"
)
_VERB_RE = re.compile(
    r"\b(?:menga\s+)?(?:iltimos,?\s+)?eslat(?:ib|gin|ing|sin)?\b(?:\s+(?:qo'y|qo'ying|qoy|yubor|yuboring|ber|bering)\w*)?"
    r"|\b(?:пожалуйста,?\s+)?(?:напомни(?:те)?|напомнить|напоминай|поставь\s+напоминание|создай\s+напоминание)(?:\s+мне)?(?!\w)"
    r"|\b(?:please\s+)?(?:remind\s+me|set\s+(?:a\s+)?reminder|reminder)(?!\w)",
    re.IGNORECASE,
)
_LEAD_RE = re.compile(r"^(?:to|about|that|чтобы|что|о|об|про)\s+", re.IGNORECASE)
_TRAIL_RE = re.compile(r"(?:\s+(?:at|on|in|by|в|во|на|к|до|через))+$", re.IGNORECASE)

_DAYPART_DEFAULT_HOUR = {"morning": 8, "noon": 12, "afternoon": 15, "evening": 19, "night": 22}


@dataclass
class ParsedWhen:
    dt_utc: datetime          # UTC (timezone'siz) — bazaga yoziladi
    local: datetime           # foydalanuvchi vaqt mintaqasidagi vaqt
    remainder: str            # vaqt iboralari olib tashlangan matn
    has_time: bool            # soat aniq ko'rsatilganmi (yoki tushunarlimi)
    relative: bool            # "30 daqiqadan keyin" kabi nisbiy vaqtmi
    assumed_time: bool = False  # faqat sana berilgan — 09:00 qo'yildi


def normalize(text: str) -> str:
    return text.translate(_APOS).lower()


def _number(raw: str) -> float:
    raw = raw.strip()
    if re.fullmatch(r"\d+(?:[.,]\d+)?", raw):
        return float(raw.replace(",", "."))
    total = 0.0
    for token in raw.split():
        if token == "yarim":
            total += 0.5
        else:
            total += _TENS_VALUES.get(token) or _UNIT_VALUES.get(token) or _TEEN_VALUES.get(token) or 0
    return total


def _unit_kind(unit: str) -> str:
    if unit.startswith(("daq", "min", "мин")):
        return "minutes"
    if unit.startswith(("soat", "hour", "hr", "час")):
        return "hours"
    if unit.startswith(("kun", "day", "дн", "ден")):
        return "days"
    if unit.startswith(("haft", "week", "недел")):
        return "weeks"
    return "months"


def _prefix_lookup(table, word: str) -> int:
    for prefix, value in table:
        if word.startswith(prefix):
            return value
    raise KeyError(word)


def _find_relative(work: str, loose: bool) -> list[re.Match] | None:
    """Ketma-ket kelgan nisbiy iboralarni zanjirga yig'adi: "1 soat 30 daqiqadan keyin"."""
    matches = list(_REL_RE.finditer(work))
    i = 0
    while i < len(matches):
        chain = [matches[i]]
        j = i + 1
        while j < len(matches) and not work[chain[-1].end():matches[j].start()].strip():
            chain.append(matches[j])
            j += 1
        if loose or chain[0].group("pre") or chain[-1].group("after"):
            return chain
        i = j
    return None


def _safe_date(year: int, month: int, day: int) -> date | None:
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _resolve_year(day: int, month: int, today: date) -> date | None:
    """Yil ko'rsatilmasa: joriy yil, o'tib ketgan bo'lsa — keyingi yil."""
    candidate = _safe_date(today.year, month, day)
    if candidate is None or candidate < today:
        candidate = _safe_date(today.year + 1, month, day) or candidate
    return candidate


def _daypart_kind(raw: str) -> str:
    raw = " ".join(raw.split())
    if raw.startswith(("tushdan keyin", "после обеда", "afternoon")):
        return "afternoon"
    if raw.startswith(("ertalab", "tong", "утр", "morning")):
        return "morning"
    if raw.startswith(("tush", "kunduz", "дн", "в обед", "noon")):
        return "noon"
    if raw.startswith(("kechqurun", "kechki", "oqshom", "вечер", "evening", "tonight")):
        return "evening"
    return "night"


def _apply_daypart(hour: int, kind: str) -> int:
    if kind in ("evening", "afternoon"):
        return hour + 12 if hour < 12 else hour
    if kind == "noon":
        return hour + 12 if 1 <= hour <= 6 else hour
    if kind == "night":
        if hour == 12:
            return 0
        return hour + 12 if 6 <= hour <= 11 else hour
    return hour  # ertalab / утром / morning


def _remainder(text: str, spans: list[tuple[int, int]]) -> str:
    """Vaqt iboralari olib tashlangan, tozalangan matn (eslatma matni uchun)."""
    src = text.translate(_APOS)
    if len(src) != len(text.lower()):
        src = text.lower()
    chars = list(src)
    for start, end in spans:
        for i in range(start, min(end, len(chars))):
            chars[i] = " "
    rest = _VERB_RE.sub(" ", "".join(chars))
    for _ in range(3):
        rest = " ".join(rest.split()).strip(" ,.;:-–—!?«»\"“”()")
        rest = _LEAD_RE.sub("", rest)
        rest = _TRAIL_RE.sub("", rest)
    return rest[:1].upper() + rest[1:] if rest else ""


def parse_when(
    text: str,
    tz: tzinfo,
    now_utc: datetime | None = None,
    loose: bool = True,
) -> ParsedWhen | None:
    """Matndan vaqtni ajratib oladi.

    loose=True  — butun matn vaqt iborasi deb qaraladi ("30 daqiqa", "kechqurun").
    loose=False — oddiy gap ichidan qidiriladi ("ertaga 9:00 da dori ich"); noaniq iboralar rad etiladi.
    """
    if not text or not text.strip():
        return None

    now_utc = (now_utc or utcnow()).replace(microsecond=0)
    now_local = to_local(now_utc, tz)
    today = now_local.date()
    original = text
    work = normalize(text)
    spans: list[tuple[int, int]] = []

    def take(match: re.Match) -> None:
        nonlocal work
        start, end = match.span()
        work = work[:start] + " " * (end - start) + work[end:]
        spans.append((start, end))

    # 0) "через час", "in half an hour"
    special = _SPECIAL_REL_RE.search(work)
    if special:
        minutes = 30 if special.group("half") else 60 if special.group("hour") else 1
        take(special)
        target = now_utc + timedelta(minutes=minutes)
        return ParsedWhen(target, to_local(target, tz), _remainder(original, spans), has_time=True, relative=True)

    # 1) nisbiy vaqt: "30 daqiqadan keyin", "через 2 часа", "in 3 days"
    chain = _find_relative(work, loose)
    rel_kind: str | None = None
    date_val: date | None = None
    weekday_based = False

    if chain:
        minutes_total = days_total = months_total = 0.0
        for m in chain:
            qty, kind_ = _number(m.group("num")), _unit_kind(m.group("unit"))
            if kind_ == "minutes":
                minutes_total += qty
            elif kind_ == "hours":
                minutes_total += qty * 60
            elif kind_ == "days":
                days_total += qty
            elif kind_ == "weeks":
                days_total += qty * 7
            else:
                months_total += qty
            take(m)
        if minutes_total + days_total + months_total <= 0:
            return None
        if minutes_total > 0:
            target = now_utc + timedelta(minutes=minutes_total, days=days_total + 30 * months_total)
            return ParsedWhen(target, to_local(target, tz), _remainder(original, spans), has_time=True, relative=True)
        if days_total > 0:
            rel_kind = "days"
            date_val = (now_local + timedelta(days=days_total)).date()
        else:
            rel_kind = "months"
            date_val = add_months(now_local, int(round(months_total))).date()
    else:
        # 2) aniq sana
        for m in _ISO_RE.finditer(work):
            d = _safe_date(int(m["y"]), int(m["m"]), int(m["d"]))
            if d:
                take(m)
                date_val = d
                break
        if date_val is None:
            for m in _TEXTDATE_RE.finditer(work):
                month, day = _prefix_lookup(_MONTH_PREFIX, m["mon"]), int(m["d"])
                d = _safe_date(int(m["y"]), month, day) if m["y"] else _resolve_year(day, month, today)
                if d:
                    take(m)
                    date_val = d
                    break
        if date_val is None:
            for m in _ENDATE_RE.finditer(work):
                month, day = _prefix_lookup(_MONTH_PREFIX, m["mon"]), int(m["d"])
                d = _safe_date(int(m["y"]), month, day) if m["y"] else _resolve_year(day, month, today)
                if d:
                    take(m)
                    date_val = d
                    break
        if date_val is None:
            for m in _NUMDATE_RE.finditer(work):
                day, month, year = int(m["d"]), int(m["m"]), m["y"]
                if m["sep"] == "-" and not year:
                    continue
                if year:
                    y = int(year)
                    d = _safe_date(y + 2000 if y < 100 else y, month, day)
                else:
                    d = _resolve_year(day, month, today)
                if d:
                    take(m)
                    date_val = d
                    break
        if date_val is None:
            m = _DAYWORD_RE.search(work)
            if m:
                word = " ".join(m["w"].split())
                if word.startswith(("bugun", "сегодня", "today")):
                    offset = 0
                elif word.startswith(("ertaga", "завтра", "tomorrow")):
                    offset = 1
                else:
                    offset = 2
                take(m)
                date_val = today + timedelta(days=offset)
        if date_val is None:
            m = _WEEKDAY_RE.search(work)
            if m:
                date_val = today + timedelta(days=(_prefix_lookup(_WEEKDAY_PREFIX, m["wd"]) - today.weekday()) % 7)
                weekday_based = True
                take(m)

    # 3) kun qismi: ertalab / утром / evening ...
    daypart: str | None = None
    m = _DAYPART_RE.search(work)
    if m:
        daypart = _daypart_kind(m["p"])
        take(m)

    # 4) kun ichidagi soat
    hour: int | None = None
    minute = 0
    kind = ""
    ampm: str | None = None

    for m in _COLON_RE.finditer(work):
        hh, mm = int(m["h"]), int(m["m"])
        if hh > 23 or mm > 59 or (m["ap"] and not 1 <= hh <= 12):
            continue
        hour, minute, kind, ampm = hh, mm, "literal", m["ap"]
        take(m)
        break
    if hour is None:
        for m in _AMPM_RE.finditer(work):
            hh = int(m["h"])
            if not 1 <= hh <= 12:
                continue
            hour, minute, kind, ampm = hh, 0, "literal", m["ap"]
            take(m)
            break
    if hour is None:
        for m in _AT_RE.finditer(work):
            hh = int(m["h"])
            if hh > 24:
                continue
            # "в 5" / "at 5" faqat qo'shimcha belgi bo'lsa ishonchli (aks holda "в 2 магазина" kabi gaplar buziladi)
            if m["kw"] in ("в", "at") and not (loose or m["sfx"] or daypart or date_val is not None):
                continue
            hour, minute, kind = hh % 24, 0, "spoken"
            take(m)
            break
    if hour is None:
        for m in _DOTTIME_RE.finditer(work):
            hh, mm = int(m["h"]), int(m["m"])
            if hh > 23 or mm > 59:
                continue
            hour, minute, kind = hh, mm, "literal"
            take(m)
            break
    if hour is None:
        for m in _BARE_RE.finditer(work):
            hh = int(m["h"])
            if hh > 24:
                continue
            hour, minute, kind = hh % 24, 0, "spoken"
            take(m)
            break

    explicit_time = hour is not None
    if rel_kind is None and date_val is None and not explicit_time and daypart is None:
        return None
    if not loose and rel_kind is None and date_val is None and not explicit_time:
        return None  # faqat "kechqurun" — oddiy gapda ishonchsiz

    assumed = False
    if explicit_time:
        h = hour  # type: ignore[assignment]
        if ampm == "pm" and h < 12:
            h += 12
        elif ampm == "am" and h == 12:
            h = 0
        elif ampm is None:
            if daypart:
                h = _apply_daypart(h, daypart)
            elif kind == "spoken" and 1 <= h <= 6:
                h += 12  # "soat 5 da" / "в 5" / "at 5" — odatda 17:00
    elif daypart:
        h, minute = _DAYPART_DEFAULT_HOUR[daypart], 0
    elif rel_kind is not None:
        h, minute = now_local.hour, now_local.minute
    else:
        h, minute, assumed = 9, 0, True  # faqat sana berilgan
    h %= 24

    day = date_val or today
    candidate = datetime.combine(day, time(h, minute), tzinfo=tz)
    if candidate <= now_local:
        if date_val is None:
            candidate = datetime.combine(today + timedelta(days=1), time(h, minute), tzinfo=tz)
        elif weekday_based:
            candidate = datetime.combine(day + timedelta(days=7), time(h, minute), tzinfo=tz)

    return ParsedWhen(
        dt_utc=to_utc(candidate),
        local=candidate,
        remainder=_remainder(original, spans),
        has_time=explicit_time or daypart is not None or rel_kind is not None,
        relative=rel_kind is not None,
        assumed_time=assumed,
    )


_HALF_HOUR_RE = re.compile(r"(?:пол\s*часа|half an hour|half hour)")
_ONE_HOUR_RE = re.compile(r"(?:час|an hour|one hour|hour)")


def parse_duration(text: str) -> timedelta | None:
    """Taymer uchun davomiylik: '25', '1:30', '90 daqiqa', '1 soat 30 daqiqa', 'yarim soat', 'полчаса', '2 hours'."""
    norm = normalize(text or "").strip()
    if not norm:
        return None
    m = re.fullmatch(r"(\d{1,3})\s*:\s*(\d{2})", norm)
    if m:
        total = timedelta(hours=int(m[1]), minutes=int(m[2]))
        return total if total > timedelta() else None
    if re.fullmatch(r"\d{1,4}", norm):
        return timedelta(minutes=int(norm)) if int(norm) > 0 else None
    if _HALF_HOUR_RE.fullmatch(norm):
        return timedelta(minutes=30)
    if _ONE_HOUR_RE.fullmatch(norm):
        return timedelta(hours=1)

    total = timedelta()
    found = False
    for m in _REL_RE.finditer(norm):
        qty, kind = _number(m.group("num")), _unit_kind(m.group("unit"))
        if kind == "minutes":
            total += timedelta(minutes=qty)
        elif kind == "hours":
            total += timedelta(hours=qty)
        elif kind == "days":
            total += timedelta(days=qty)
        elif kind == "weeks":
            total += timedelta(weeks=qty)
        else:
            total += timedelta(days=30 * qty)
        found = True
    return total if found and total > timedelta() else None


_CATEGORY_WORDS = (
    ("medicine", ("dori", "tabletka", "vitamin", "ukol", "kapsula", "sirop", "tomchi", "antibiotik", "insulin",
                  "shifokor", "vrach", "doktor", "poliklinika", "kasalxona",
                  "лекарств", "таблетк", "врач", "доктор", "поликлиник", "стоматолог", "витамин",
                  "pill", "medicine", "medication", "doctor", "dentist", "pharmacy", "clinic")),
    ("meeting", ("uchrashuv", "uchrash", "yig'ilish", "majlis", "meeting", "intervyu", "suhbat", "konferensiya",
                 "taqdimot", "mijoz", "встреч", "совещани", "собеседован", "переговор", "созвон",
                 "interview", "appointment", "conference", "presentation", "client")),
    ("task", ("vazifa", "topshiriq", "topshir", "hisobot", "to'lov", "to'lash", "loyiha", "uy ishi", "muddat",
              "задач", "отчёт", "отчет", "оплат", "проект", "дедлайн", "срок",
              "task", "report", "invoice", "deadline", "project", "homework", "pay ")),
    ("plan", ("reja", "sport", "mashq", "yugur", "sayohat", "safar", "tug'ilgan kun", "bayram", "kitob", "o'qish",
              "dam olish", "план", "спорт", "тренировк", "поездк", "день рождения", "отпуск", "книг",
              "gym", "workout", "trip", "birthday", "holiday", "vacation", "plan", "run ")),
)


def guess_category(text: str) -> str:
    """Matndagi kalit so'zlarga qarab eslatma turini taxmin qiladi."""
    norm = normalize(text or "") + " "
    for category, words in _CATEGORY_WORDS:
        if any(word in norm for word in words):
            return category
    return "other"
