"""Pul summalarini tushunish ("85 ming", "1.2 mln", "$12") va chiroyli ko'rsatish (so'm / dollar)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

MAX_UZS = 10**12   # 1 trillion so'm
MAX_USD = 10**9

_APOS = str.maketrans({"\u2018": "'", "\u2019": "'", "\u02bb": "'", "\u02bc": "'", "`": "'", "\u00b4": "'"})

_NUM = r"\d{1,3}(?:[ \u00a0.,]\d{3})+(?:[.,]\d+)?|\d+(?:[.,]\d+)?"
_UNIT = (
    r"(?:(?:mlrd|млрд|billion|million|миллион|mln|млн|ming|тысяч|thousand)\w*|(?:mil|тыс|k|к)(?!\w)\.?)"
)
_CUR_USD = r"(?:\$|usd(?!\w)|dollar\w*|доллар\w*|долл\.?|бакс\w*)"
_CUR_UZS = r"(?:so'?m(?!\w)|som(?!\w)|sum(?!\w)|сум\w*|uzs(?!\w))"
_CUR = rf"(?:{_CUR_USD}|{_CUR_UZS})"

_END_RE = re.compile(
    rf"(?:(?<=\s)|^)(?P<pre>\$\s*)?(?P<num>{_NUM})\s*(?P<unit>{_UNIT})?\s*(?P<cur>{_CUR})?\s*$", re.IGNORECASE
)
_START_RE = re.compile(
    rf"^\s*(?P<pre>\$\s*)?(?P<num>{_NUM})\s*(?P<unit>{_UNIT})?\s*(?P<cur>{_CUR})?(?=\s|$)", re.IGNORECASE
)
_FULL_RE = re.compile(
    rf"^\s*(?P<pre>\$\s*)?(?P<num>{_NUM})\s*(?P<unit>{_UNIT})?\s*(?P<cur>{_CUR})?\s*$", re.IGNORECASE
)
_BULLET_RE = re.compile(r"^\s*(?:[•\-–—*·]+|\d{1,2}[.)])\s+")
_USD_RE = re.compile(_CUR_USD, re.IGNORECASE)


@dataclass(frozen=True)
class Amount:
    value: Decimal      # kiritilgan valyutada (so'm yoki dollar)
    currency: str       # "uzs" | "usd"


@dataclass(frozen=True)
class ExpenseLine:
    name: str
    amount: Amount | None
    bad_amount: bool = False   # raqam bor, lekin yaroqsiz (0, juda katta)


def _multiplier(unit: str) -> int:
    unit = unit.lower()
    if unit.startswith(("mlrd", "млрд", "billion")):
        return 10**9
    if unit.startswith(("mln", "млн", "million", "миллион", "mil")):
        return 10**6
    if unit:
        return 10**3
    return 1


def _to_decimal(raw: str, has_unit: bool) -> Decimal | None:
    compact = raw.replace("\u00a0", " ").replace(" ", "")
    dots, commas = compact.count("."), compact.count(",")
    if dots and commas:  # oxirgi ajratgich — o'nlik
        last = max(compact.rfind("."), compact.rfind(","))
        value = re.sub(r"[.,]", "", compact[:last]) + "." + compact[last + 1:]
    elif dots + commas > 1:  # 1.250.000 — minglik ajratgichlar
        value = re.sub(r"[.,]", "", compact)
    elif dots + commas == 1:
        sep = "." if dots else ","
        left, right = compact.split(sep)
        if len(right) == 3 and not has_unit and len(left) <= 3 and left != "0":
            value = left + right  # 5.000 -> 5000
        else:
            value = f"{left}.{right}"
    else:
        value = compact
    try:
        return Decimal(value)
    except Exception:  # noqa: BLE001
        return None


def _build(m: re.Match) -> Amount | None:
    unit = m.group("unit") or ""
    cur = m.group("cur") or ""
    value = _to_decimal(m.group("num"), bool(unit))
    if value is None or value <= 0:
        return None
    value *= _multiplier(unit)
    is_usd = bool(m.group("pre")) or bool(cur and _USD_RE.fullmatch(cur.strip()))
    if is_usd:
        value = value.quantize(Decimal("0.01"), ROUND_HALF_UP)
        return Amount(value, "usd") if 0 < value <= MAX_USD else None
    value = value.quantize(Decimal(1), ROUND_HALF_UP)
    return Amount(value, "uzs") if 0 < value <= MAX_UZS else None


def normalize(text: str) -> str:
    return text.translate(_APOS)


def parse_amount(text: str) -> Amount | None:
    """Faqat summadan iborat matn: '5000', '85 ming', '1.2 mln', '$12', '2 млн'."""
    m = _FULL_RE.match(normalize(text or ""))
    return _build(m) if m else None


def parse_expense_line(line: str) -> ExpenseLine | None:
    """'Non 5000' -> (nom, summa). Faqat nom ('Non') yoki faqat summa ('5000') ham qabul qilinadi."""
    line = _BULLET_RE.sub("", normalize(line or "")).strip()
    if not line:
        return None
    m = _END_RE.search(line)
    if m:
        name = line[: m.start()]
    else:
        m = _START_RE.match(line)
        name = line[m.end():] if m else line
    amount = _build(m) if m else None
    name = " ".join(name.strip(" -–—:,.;•*«»\"").split())
    return ExpenseLine(name=name, amount=amount, bad_amount=bool(m and amount is None))


def parse_expense_lines(text: str, limit: int = 30) -> list[ExpenseLine]:
    """Har bir qator (yoki ';' bilan ajratilgan qism) — bitta mahsulot."""
    lines = [part for part in re.split(r"[\n;]+", text or "") if part.strip()]
    return [parsed for part in lines[:limit] if (parsed := parse_expense_line(part)) is not None]


# ---------------------------------------------------------------- ko'rsatish
def group_digits(n: int) -> str:
    return f"{abs(int(n)):,}".replace(",", " ")


def fmt_sum(n: int, lang: str = "uz") -> str:
    """1250000 -> '1 250 000 so'm' / '1 250 000 сум' / '1,250,000 UZS'."""
    sign = "−" if n < 0 else ""
    if lang == "en":
        return f"{sign}{abs(int(n)):,} UZS"
    return f"{sign}{group_digits(n)} {'so' + chr(39) + 'm' if lang == 'uz' else 'сум'}"


def usd_value(amount_uzs: int, rate: Decimal | None) -> Decimal | None:
    if not rate or rate <= 0:
        return None
    return (Decimal(int(amount_uzs)) / rate).quantize(Decimal("0.01"), ROUND_HALF_UP)


def fmt_usd(amount_uzs: int, rate: Decimal | None) -> str | None:
    """So'm summasining dollardagi qiymati: '$98.52' (kurs bo'lmasa None)."""
    usd = usd_value(amount_uzs, rate)
    if usd is None:
        return None
    sign = "−" if usd < 0 else ""
    return f"{sign}${abs(usd):,.2f}"


def fmt_rate(rate: Decimal, lang: str = "uz") -> str:
    text = f"{rate:,.2f}"
    return text if lang == "en" else text.replace(",", " ")


def to_uzs(amount: Amount, rate: Decimal | None) -> int | None:
    """Dollarda kiritilgan summani so'mga o'giradi (kurs kerak)."""
    if amount.currency == "uzs":
        return int(amount.value)
    if not rate or rate <= 0:
        return None
    uzs = int((amount.value * rate).quantize(Decimal(1), ROUND_HALF_UP))
    return uzs if 0 < uzs <= MAX_UZS else None
