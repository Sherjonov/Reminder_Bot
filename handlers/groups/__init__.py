from aiogram import Router

from filters import groups_only

from . import group_reminders


def setup_group_router() -> Router:
    router = Router(name="groups")
    groups_only(router)
    router.include_router(group_reminders.router)
    return router
