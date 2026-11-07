"""USD/UZS kursi: O'zbekiston Markaziy banki (CBU) dan olinadi, bazada keshlanadi.

Asosiy manba — CBU rasmiy JSON API. U ishlamasa, zaxira manba (open.er-api.com) ishlatiladi.
Internet bo'lmaganda oxirgi saqlangan kurs (baza keshi) ishlatiladi.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from email.utils import parsedate_to_datetime

import aiohttp

from services.db_api import db
from services.db_api import finance as fin
from services.misc.timeutils import utcnow

logger = logging.getLogger(__name__)

CBU_URLS = (
    "https://cbu.uz/uz/arkhiv-kursov-valyut/json/USD/",
    "https://cbu.uz/ru/arkhiv-kursov-valyut/json/USD/",
)
FALLBACK_URL = "https://open.er-api.com/v6/latest/USD"
REFRESH_OK = 3 * 3600      # muvaffaqiyatli bo'lsa 3 soatdan keyin yana
REFRESH_FAIL = 10 * 60     # xato bo'lsa 10 daqiqadan keyin qayta urinadi
MIN_RATE, MAX_RATE = Decimal(1000), Decimal(100000)  # mantiqiy chegaralar (1 $ = ? so'm)


def _decimal(value) -> Decimal | None:
    try:
        rate = Decimal(str(value).replace(" ", "").replace(",", "."))
    except (InvalidOperation, ValueError):
        return None
    return rate if MIN_RATE <= rate <= MAX_RATE else None


class CurrencyService:
    def __init__(self) -> None:
        self.rate: Decimal | None = None
        self.rate_date: date | None = None
        self.source = ""
        self.fetched_at: datetime | None = None
        self._task: asyncio.Task | None = None

    # ------------------------------------------------------------------ kesh
    async def load_cached(self) -> None:
        row = await fin.get_rate(db, "USD")
        if row:
            self.rate = Decimal(str(row["rate"]))
            self.rate_date = row["rate_date"]
            self.source = row["source"]
            self.fetched_at = row["fetched_at"]

    def set_rate(self, rate: Decimal, rate_date: date | None, source: str) -> None:
        self.rate, self.rate_date, self.source, self.fetched_at = rate, rate_date, source, utcnow()

    # ------------------------------------------------------------------ manbalar
    @staticmethod
    async def _from_cbu(session: aiohttp.ClientSession) -> tuple[Decimal, date | None, str] | None:
        for url in CBU_URLS:
            try:
                async with session.get(url) as resp:
                    resp.raise_for_status()
                    data = await resp.json(content_type=None)
            except Exception as exc:  # noqa: BLE001 — keyingi manzilni sinab ko'ramiz
                logger.warning("CBU manzili ishlamadi (%s): %s", url, exc)
                continue
            best: tuple[date, Decimal] | None = None
            for item in data if isinstance(data, list) else []:
                if str(item.get("Ccy", "")).upper() != "USD":
                    continue
                rate = _decimal(item.get("Rate"))
                try:
                    day = datetime.strptime(str(item.get("Date")), "%d.%m.%Y").date()
                except ValueError:
                    day = date.min
                if rate and (best is None or day >= best[0]):
                    best = (day, rate)
            if best:
                return best[1], (None if best[0] == date.min else best[0]), "CBU"
        return None

    @staticmethod
    async def _from_fallback(session: aiohttp.ClientSession) -> tuple[Decimal, date | None, str] | None:
        async with session.get(FALLBACK_URL) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)
        rate = _decimal((data.get("rates") or {}).get("UZS"))
        if not rate:
            return None
        day = None
        if data.get("time_last_update_utc"):
            try:
                day = parsedate_to_datetime(data["time_last_update_utc"]).date()
            except (TypeError, ValueError):
                day = None
        return rate, day, "er-api"

    async def refresh(self) -> bool:
        """Kursni internetdan yangilaydi. Muvaffaqiyatli bo'lsa True."""
        timeout = aiohttp.ClientTimeout(total=12)
        async with aiohttp.ClientSession(timeout=timeout, headers={"User-Agent": "EslatmaBot/2.0"}) as session:
            for fetcher in (self._from_cbu, self._from_fallback):
                try:
                    result = await fetcher(session)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Kurs manbasi ishlamadi (%s): %s", fetcher.__name__, exc)
                    continue
                if result:
                    rate, rate_date, source = result
                    self.set_rate(rate, rate_date, source)
                    await fin.save_rate(db, "USD", rate, rate_date, source, utcnow())
                    logger.info("Dollar kursi yangilandi: 1 $ = %s so'm (%s, %s)", rate, source, rate_date)
                    return True
        return False

    # ------------------------------------------------------------------ fon vazifasi
    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run(), name="currency-refresh")

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run(self) -> None:
        while True:
            try:
                ok = await self.refresh()
            except asyncio.CancelledError:
                raise
            except Exception:  # noqa: BLE001
                logger.exception("Kursni yangilashda xatolik")
                ok = False
            await asyncio.sleep(REFRESH_OK if ok else REFRESH_FAIL)


currency = CurrencyService()
