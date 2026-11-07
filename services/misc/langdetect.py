"""Foydalanuvchi qaysi tilda yozayotganini aniqlash (o'zbekcha / ruscha / inglizcha).

Faqat ishonchli belgi bo'lsa til qaytariladi; aks holda None (joriy til saqlanib qoladi).
"""
from __future__ import annotations

import re

from .i18n import label_language

_APOS = str.maketrans({"\u2018": "'", "\u2019": "'", "\u02bb": "'", "\u02bc": "'", "`": "'", "\u00b4": "'"})
_WORD_RE = re.compile(r"[a-z]+(?:'[a-z]+)*")
_UZ_APOS_RE = re.compile(r"[a-z][og]'")

UZ_WORDS = set("""
salom assalomu alaykum rahmat raxmat ha yo'q yoq bor men menda sen siz biz bu shu va bilan uchun lekin yoki ham
hozir bugun ertaga indin kecha soat daqiqa daqiqadan soatdan kundan keyin oldin eslat eslatib eslatma eslatmalar
yangi bekor saqlash o'chirish ro'yxat sozlamalar yordam taymer vazifa dori uchrashuv reja xarajat xarajatlar
narx narxi mahsulot mahsulotlar pul pulim summa umumiy so'm som sum ming mln qancha necha nima qayerda qachon kerak
boshla boshlash tayyor bajarildi kechiktirish dushanba seshanba chorshanba payshanba juma shanba yakshanba
yanvar fevral mart aprel iyun iyul avgust sentabr oktabr noyabr dekabr kechqurun ertalab tushda kechasi
non sut go'sht gosht tuxum yog' guruch shakar choy sabzi piyoz kartoshka pomidor olma banan meva sabzavot
benzin kitob kiyim poyabzal ovqat tushlik kechki nonushta qo'sh qosh qo'shish ayir qoldiq balans
shifokorga borishni eslatib qo'y qo'ng'iroq onamga dadamga do'stim ish uy bozor bozorga dukon
""".split())

EN_WORDS = set("""
hello hi hey thanks thank please yes no i me my you your we the an and or but for with to at on in of by
from this that it is are am be was were remind reminder reminders tomorrow today tonight yesterday morning evening
afternoon night noon minutes minute hours hour days day weeks week months month later after before next every
daily weekly monthly new add delete remove edit cancel save list settings help timer task tasks meeting meetings
medicine pills pill doctor call buy bought spent expense expenses balance total amount money price cost paid pay
payment bread milk meat eggs rice sugar tea coffee taxi gas fuel book clothes shoes phone lunch dinner breakfast
monday tuesday wednesday thursday friday saturday sunday january february march april june july august september
october november december groceries shopping coffee
""".split())


def detect_language(text: str) -> str | None:
    """'uz' | 'ru' | 'en' yoki None (aniqlab bo'lmadi)."""
    if not text:
        return None
    by_label = label_language(text)
    if by_label:
        return by_label

    low = text.lower().translate(_APOS)
    letters = [c for c in low if c.isalpha()]
    if len(letters) < 2:
        return None

    cyrillic = sum(1 for c in letters if "\u0400" <= c <= "\u04ff")
    if cyrillic / len(letters) >= 0.5:
        return "uz" if any(c in "ўқғҳ" for c in low) else "ru"

    words = _WORD_RE.findall(low)
    uz_score = sum(1 for w in words if w in UZ_WORDS) + 2 * len(_UZ_APOS_RE.findall(low))
    en_score = sum(1 for w in words if w in EN_WORDS)
    if uz_score > en_score:
        return "uz"
    if en_score > uz_score:
        return "en"
    return None
