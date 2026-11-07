"""Routerlarni chat turiga (shaxsiy / guruh / admin) bog'lovchi yordamchilar.

Filtr har bir "barg" routerga alohida qo'yiladi — aiogram versiyasidan qat'i nazar ishonchli ishlaydi.
"""
from aiogram import F, Router

from .is_admin import IsAdmin

_GROUP_TYPES = {"group", "supergroup"}


def private_only(router: Router) -> Router:
    router.message.filter(F.chat.type == "private")
    router.callback_query.filter(F.message.chat.type == "private")
    return router


def groups_only(router: Router) -> Router:
    router.message.filter(F.chat.type.in_(_GROUP_TYPES))
    router.callback_query.filter(F.message.chat.type.in_(_GROUP_TYPES))
    router.my_chat_member.filter(F.chat.type.in_(_GROUP_TYPES))
    return router


def admins_only(router: Router) -> Router:
    router.message.filter(IsAdmin(), F.chat.type == "private")
    router.callback_query.filter(IsAdmin())
    return router
