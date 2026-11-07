"""Soatni Telegram serveri vaqtiga moslash.

Muammo: bot kompyuter soatiga tayanadi. Windows'da vaqt mintaqasi noto'g'ri qo'yilgan bo'lsa (masalan, UTC+03 o'rniga
UTC+05) va vaqt qo'lda to'g'rilangan bo'lsa, kompyuterning UTC vaqti xato bo'ladi va bot soatni 2 soat oldinga/orqaga
ko'rsatadi. Yechim: server javobidagi `Date` sarlavhasi (har doim aniq UTC) bilan solishtirib, farqni (offset) topamiz
va `utcnow()` ga qo'shamiz. Shunda kompyuter sozlamalari qanday bo'lmasin, bot haqiqiy vaqt bilan ishlaydi.
"""
from __future__ import annotations

import asyncio
import logging
import time
from datetime import timedelta
from email.utils import parsedate_to_datetime

import aiohttp

from services.misc.timeutils import get_clock_offset, set_clock_offset

logger = logging.getLogger(__name__)

SOURCES = (
    "https://api.telegram.org",
    "https://cbu.uz",
    "https://www.cloudflare.com",
    "https://www.google.com",
)
RESYNC_SECONDS = 30 * 60
IGNORE_BELOW = 2.0  # soniya: bundan kichik farqni e'tiborsiz qoldiramiz


async def measure_offset(session: aiohttp.ClientSession, url: str) -> float | None:
    """Serverning `Date` sarlavhasiga ko'ra (server vaqti - kompyuter vaqti) ni soniyada qaytaradi."""
    started = time.time()
    async with session.get(url, allow_redirects=False, timeout=aiohttp.ClientTimeout(total=8)) as resp:
        finished = time.time()
        header = resp.headers.get("Date")
    if not header:
        return None
    server_ts = parsedate_to_datetime(header).timestamp() + 0.5  # Date 1 soniyagacha yaxlitlangan
    host_ts = started + (finished - started) / 2
    return server_ts - host_ts


class TimeSync:
    def __init__(self, sources: tuple[str, ...] = SOURCES) -> None:
        self.sources = sources
        self.source: str | None = None
        self.synced = False
        self._task: asyncio.Task | None = None

    @property
    def offset(self) -> timedelta:
        return get_clock_offset()

    async def sync_once(self) -> bool:
        async with aiohttp.ClientSession() as session:
            for url in self.sources:
                try:
                    diff = await measure_offset(session, url)
                except Exception as exc:  # noqa: BLE001
                    logger.debug("Vaqt manbasi %s ishlamadi: %s", url, exc)
                    continue
                if diff is None:
                    continue
                # diff — kompyuterning xom soati (time.time) va server vaqti orasidagi to'liq farq
                offset = timedelta(seconds=round(diff)) if abs(diff) >= IGNORE_BELOW else timedelta(0)
                if offset:
                    logger.warning(
                        "Kompyuter soati server vaqtidan %s farq qiladi — bot vaqtni avtomatik tuzatdi (manba: %s).",
                        offset, url,
                    )
                set_clock_offset(offset)
                self.source, self.synced = url, True
                return True
        logger.warning("Soatni server vaqti bilan solishtirib bo'lmadi — kompyuter soati ishlatiladi.")
        return False

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run(), name="time-sync")

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
            await asyncio.sleep(RESYNC_SECONDS)
            try:
                await self.sync_once()
            except asyncio.CancelledError:
                raise
            except Exception:  # noqa: BLE001
                logger.exception("Vaqtni sinxronlashda xatolik")


time_sync = TimeSync()  # umumiy nusxa: main.py ishga tushiradi, /vaqt buyrug'i ma'lumot oladi
