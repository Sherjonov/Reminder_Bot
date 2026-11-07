"""MySQL / MariaDB bilan asinxron ishlash (aiomysql ulanishlar puli)."""
from __future__ import annotations

import asyncio
import logging
import re
import warnings
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator, Awaitable, Callable, Sequence, TypeVar

import aiomysql
from pymysql.err import Warning as MySQLWarning

from config import settings

logger = logging.getLogger(__name__)

# "IF NOT EXISTS" tufayli chiqadigan ma'lumot xabarlarini (masalan: Table already exists) ekranga chiqarmaymiz
warnings.filterwarnings("ignore", category=MySQLWarning)

SCHEMA_PATH = Path(__file__).with_name("schema.sql")
_DB_NAME_RE = re.compile(r"^[A-Za-z0-9_]+$")
T = TypeVar("T")

# Eski bazalarga yangi ustunlarni qo'shish (CREATE TABLE IF NOT EXISTS mavjud jadvalga tegmaydi)
MIGRATIONS: tuple[tuple[str, str, str], ...] = (
    ("users", "language", "VARCHAR(2) NOT NULL DEFAULT 'uz'"),
)
_DEADLOCK_CODES = (1205, 1213)


class Transaction:
    """Bitta ulanishdagi tranzaksiya: execute / insert / fetchone / fetchall (Database bilan bir xil interfeys)."""

    def __init__(self, conn: aiomysql.Connection) -> None:
        self._conn = conn

    async def _run(self, sql: str, args: Sequence[Any] | None, mode: str) -> Any:
        async with self._conn.cursor() as cur:
            await cur.execute(sql, args)
            if mode == "one":
                return await cur.fetchone()
            if mode == "all":
                return list(await cur.fetchall())
            if mode == "insert":
                return cur.lastrowid
            return cur.rowcount

    async def execute(self, sql: str, args: Sequence[Any] | None = None) -> int:
        return await self._run(sql, args, "exec")

    async def insert(self, sql: str, args: Sequence[Any] | None = None) -> int:
        return await self._run(sql, args, "insert")

    async def fetchone(self, sql: str, args: Sequence[Any] | None = None) -> dict | None:
        return await self._run(sql, args, "one")

    async def fetchall(self, sql: str, args: Sequence[Any] | None = None) -> list[dict]:
        return await self._run(sql, args, "all")


class Database:
    """aiomysql puli ustidagi yupqa qobiq: execute / insert / fetchone / fetchall."""

    def __init__(self) -> None:
        self.pool: aiomysql.Pool | None = None

    # ------------------------------------------------------------------ ulanish
    async def connect(self) -> None:
        if not _DB_NAME_RE.match(settings.db_name):
            raise RuntimeError("DB_NAME faqat lotin harflari, raqam va _ dan iborat bo'lishi kerak")
        await self._ensure_database()
        self.pool = await aiomysql.create_pool(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            db=settings.db_name,
            charset="utf8mb4",
            autocommit=True,
            minsize=1,
            maxsize=10,
            pool_recycle=1800,
            connect_timeout=10,
            cursorclass=aiomysql.DictCursor,
        )
        logger.info("MySQL ulandi: %s@%s:%s/%s", settings.db_user, settings.db_host, settings.db_port, settings.db_name)

    async def _ensure_database(self) -> None:
        """Baza yo'q bo'lsa yaratadi (huquq bo'lmasa — jim o'tib ketadi)."""
        try:
            conn = await aiomysql.connect(
                host=settings.db_host,
                port=settings.db_port,
                user=settings.db_user,
                password=settings.db_password,
                charset="utf8mb4",
                autocommit=True,
                connect_timeout=10,
            )
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        f"CREATE DATABASE IF NOT EXISTS `{settings.db_name}` "
                        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                    )
            finally:
                conn.close()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Bazani tekshirib bo'lmadi (%s) — mavjud deb hisoblayman", exc)

    async def init_schema(self) -> None:
        """schema.sql dagi jadvallarni yaratadi (mavjud bo'lsa tegmaydi)."""
        sql = SCHEMA_PATH.read_text(encoding="utf-8")
        sql = re.sub(r"--[^\n]*", "", sql)
        for statement in (part.strip() for part in sql.split(";")):
            if statement:
                await self.execute(statement)
        for table, column, ddl in MIGRATIONS:
            found = await self.fetchone(
                "SELECT COUNT(*) AS c FROM information_schema.columns "
                "WHERE table_schema = DATABASE() AND table_name = %s AND column_name = %s",
                (table, column),
            )
            if not found or not found["c"]:
                await self.execute(f"ALTER TABLE `{table}` ADD COLUMN `{column}` {ddl}")
                logger.info("Migratsiya: %s.%s qo'shildi", table, column)
        logger.info("Jadvallar tayyor")

    async def close(self) -> None:
        if self.pool is not None:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None

    # ------------------------------------------------------------------ so'rovlar
    async def _run(self, sql: str, args: Sequence[Any] | None, mode: str) -> Any:
        if self.pool is None:
            raise RuntimeError("Baza ulanmagan: avval db.connect() ni chaqiring")
        for attempt in (1, 2):
            try:
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(sql, args)
                        if mode == "one":
                            return await cur.fetchone()
                        if mode == "all":
                            return list(await cur.fetchall())
                        if mode == "insert":
                            return cur.lastrowid
                        return cur.rowcount
            except (aiomysql.OperationalError, aiomysql.InterfaceError) as exc:
                if attempt == 2:
                    raise
                logger.warning("MySQL aloqasi uzildi (%s), qayta urinaman", exc)
                await asyncio.sleep(0.5)

    async def execute(self, sql: str, args: Sequence[Any] | None = None) -> int:
        """Ta'sirlangan qatorlar sonini qaytaradi."""
        return await self._run(sql, args, "exec")

    async def insert(self, sql: str, args: Sequence[Any] | None = None) -> int:
        """Yangi qatorning AUTO_INCREMENT ID sini qaytaradi."""
        return await self._run(sql, args, "insert")

    async def fetchone(self, sql: str, args: Sequence[Any] | None = None) -> dict | None:
        return await self._run(sql, args, "one")

    async def fetchall(self, sql: str, args: Sequence[Any] | None = None) -> list[dict]:
        return await self._run(sql, args, "all")

    # ------------------------------------------------------------------ tranzaksiyalar
    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[Transaction]:
        """`async with db.transaction() as tx:` — ichidagi barcha so'rovlar yoki birga bajariladi, yoki birga bekor bo'ladi."""
        if self.pool is None:
            raise RuntimeError("Baza ulanmagan: avval db.connect() ni chaqiring")
        async with self.pool.acquire() as conn:
            await conn.begin()
            try:
                yield Transaction(conn)
            except BaseException:
                await conn.rollback()
                raise
            else:
                await conn.commit()

    async def run_in_transaction(self, func: Callable[[Transaction], Awaitable[T]], retries: int = 3) -> T:
        """Tranzaksiyada `func(tx)` ni bajaradi; deadlock bo'lsa qayta urinadi."""
        for attempt in range(1, retries + 1):
            try:
                async with self.transaction() as tx:
                    return await func(tx)
            except aiomysql.OperationalError as exc:
                if exc.args and exc.args[0] in _DEADLOCK_CODES and attempt < retries:
                    logger.warning("Deadlock, qayta urinaman (%s/%s)", attempt, retries)
                    await asyncio.sleep(0.1 * attempt)
                    continue
                raise
        raise RuntimeError("unreachable")

    async def ping(self) -> bool:
        try:
            await self.fetchone("SELECT 1 AS ok")
            return True
        except Exception:  # noqa: BLE001
            return False


db = Database()
