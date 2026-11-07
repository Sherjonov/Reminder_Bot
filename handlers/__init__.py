"""Barcha routerlar shu yerda yig'iladi.

Tartib: xatolar -> adminlar -> guruhlar -> foydalanuvchilar (ichida: menyu -> suhbat bosqichlari -> fallback).
"""
from aiogram import Router

from . import errors
from .admins import setup_admin_router
from .groups import setup_group_router
from .users import setup_user_router


def setup_routers() -> Router:
    root = Router(name="root")
    root.include_routers(
        errors.router,
        setup_admin_router(),
        setup_group_router(),
        setup_user_router(),
    )
    return root


__all__ = ["setup_routers"]
