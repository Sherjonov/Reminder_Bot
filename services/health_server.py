"""Kichik HTTP server: Render/Railway kabi hostinglar "port ochiq" ekanini tekshiradi.

GET /        -> "Eslatma Bot ishlayapti"
GET /health  -> {"status": "ok", "db": true}
"""
from __future__ import annotations

import logging

from aiohttp import web

from config import settings
from services.db_api import db
from services.misc.timeutils import utcnow

logger = logging.getLogger(__name__)


class HealthServer:
    def __init__(self) -> None:
        self._runner: web.AppRunner | None = None

    async def start(self) -> None:
        if not settings.health_enabled:
            return
        app = web.Application()
        app.router.add_get("/", self._index)
        app.router.add_get("/health", self._health)
        runner = web.AppRunner(app, access_log=None)
        await runner.setup()
        try:
            await web.TCPSite(runner, settings.health_host, settings.health_port).start()
        except OSError as exc:  # port band bo'lsa botning o'zi to'xtab qolmasin
            logger.warning("Health server ishga tushmadi (port %s band?): %s", settings.health_port, exc)
            await runner.cleanup()
            return
        self._runner = runner
        logger.info("Health server: http://%s:%s/health", settings.health_host, settings.health_port)

    async def stop(self) -> None:
        if self._runner is not None:
            await self._runner.cleanup()
            self._runner = None

    @staticmethod
    async def _index(request: web.Request) -> web.Response:
        return web.Response(text="Eslatma Bot ishlayapti ⏰")

    @staticmethod
    async def _health(request: web.Request) -> web.Response:
        db_ok = await db.ping()
        payload = {"status": "ok" if db_ok else "degraded", "db": db_ok, "time": utcnow().isoformat() + "Z"}
        return web.json_response(payload, status=200 if db_ok else 503)
