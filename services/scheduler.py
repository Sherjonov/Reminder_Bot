"""Eslatmalarni vaqtida yuboruvchi rejalashtirgich.

Har `SCHEDULER_TICK` soniyada bazadan vaqti kelgan eslatmalar olinib yuboriladi.
Eslatmalar bazada saqlanadi, shuning uchun bot o'chib-yonganda ham hech narsa yo'qolmaydi
(bot o'chiq paytda kelgan eslatmalar yoqilganda "kechikib yetkazildi" belgisi bilan yuboriladi).
"""
from __future__ import annotations

import asyncio
import logging
import time as clock
from datetime import datetime, time, timedelta

from aiogram import Bot

from config import settings
from keyboards.inline.reminders import fired_kb
from services.db_api import reminders as rem_db
from services.db_api import users as user_db
from services.messaging import SEND_BAD, SEND_BLOCKED, SEND_OK, safe_send
from services.misc.formatting import digest_text, esc, fired_text
from services.misc.recurrence import next_occurrence
from services.misc.timeutils import get_tz, to_local, to_utc, utcnow

logger = logging.getLogger(__name__)

BATCH = 100
PURGE_AFTER_DAYS = 30


class ReminderScheduler:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self._task: asyncio.Task | None = None
        self._last_digest = 0.0
        self._last_purge = 0.0

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run(), name="reminder-scheduler")

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run(self) -> None:
        logger.info("Rejalashtirgich ishga tushdi (har %s soniyada tekshiradi)", settings.scheduler_tick)
        while True:
            try:
                await self.process_due()
                now = clock.monotonic()
                if now - self._last_digest >= 60:
                    self._last_digest = now
                    await self.process_digests()
                if now - self._last_purge >= 6 * 3600:
                    self._last_purge = now
                    removed = await rem_db.purge_old(utcnow() - timedelta(days=PURGE_AFTER_DAYS))
                    if removed:
                        logger.info("%s ta eski eslatma tozalandi", removed)
            except asyncio.CancelledError:
                raise
            except Exception:  # noqa: BLE001 — rejalashtirgich hech qachon to'xtab qolmasligi kerak
                logger.exception("Rejalashtirgichda xatolik")
            await asyncio.sleep(settings.scheduler_tick)

    # ------------------------------------------------------------------ eslatmalar
    async def process_due(self) -> int:
        """Vaqti kelgan eslatmalarni yuboradi. Ishlangan eslatmalar sonini qaytaradi."""
        handled = 0
        while True:
            now = utcnow()
            rows = await rem_db.due(now, BATCH)
            progressed = 0
            for rem in rows:
                if await self._fire(rem, now):
                    progressed += 1
                handled += 1
                await asyncio.sleep(0.04)
            if len(rows) < BATCH or progressed == 0:
                return handled

    async def _fire(self, rem: dict, now: datetime) -> bool:
        """Bitta eslatmani yuboradi. Holati o'zgargan bo'lsa True (aks holda keyingi aylanishda qayta uriniladi)."""
        tz = get_tz(rem["timezone"])
        is_private = rem["chat_id"] == rem["user_id"]
        late = (now - rem["remind_at"]).total_seconds()

        mention = None
        if not is_private:
            name = esc(rem.get("full_name") or "Foydalanuvchi")
            mention = f'<a href="tg://user?id={rem["user_id"]}">{name}</a>'

        lang = rem.get("language") or "uz"
        text = fired_text(rem, tz, lang, late, mention)
        markup = fired_kb(rem, lang) if is_private else None
        result = await safe_send(self.bot, rem["chat_id"], text, reply_markup=markup)

        if result == SEND_OK:
            await self._after_sent(rem, now)
            return True
        if result == SEND_BLOCKED:
            if is_private:
                await user_db.set_blocked(rem["user_id"], True)
            await rem_db.fail_all_for_chat(rem["chat_id"])
            return True
        if result == SEND_BAD:
            await rem_db.mark_failed(rem["id"])
            return True
        return False

    @staticmethod
    async def _after_sent(rem: dict, now: datetime) -> None:
        if rem["repeat_type"] == "none":
            await rem_db.mark_sent(rem["id"], now)
            return
        following = next_occurrence(rem["remind_at"], rem["repeat_type"], rem["repeat_value"], rem["timezone"], now)
        if following is None:
            await rem_db.mark_sent(rem["id"], now)
        else:
            await rem_db.advance(rem["id"], following, now)

    # ------------------------------------------------------------------ kunlik xulosa
    async def process_digests(self) -> None:
        """Yoqilgan foydalanuvchilarga ertalab bugungi eslatmalar ro'yxatini yuboradi."""
        now = utcnow()
        for user in await user_db.digest_candidates():
            tz = get_tz(user["timezone"])
            local = to_local(now, tz)
            if not (settings.digest_hour <= local.hour < settings.digest_hour + 3):
                continue
            if user["last_digest_date"] == local.date():
                continue
            midnight = datetime.combine(local.date() + timedelta(days=1), time(0, 0), tzinfo=tz)
            items = await rem_db.list_between(user["user_id"], now, to_utc(midnight))
            await user_db.set_digest_date(user["user_id"], local.date())
            if not items:
                continue
            result = await safe_send(self.bot, user["user_id"], digest_text(items, tz, user.get("language") or "uz"))
            if result == SEND_BLOCKED:
                await user_db.set_blocked(user["user_id"], True)
            await asyncio.sleep(0.04)
