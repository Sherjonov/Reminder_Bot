from aiogram import Router

from filters import admins_only

from . import broadcast, panel


def setup_admin_router() -> Router:
    router = Router(name="admins")
    admins_only(router)  # ehtiyot uchun: barg routerlarda ham shu filtr bor
    router.include_routers(panel.router, broadcast.router)
    return router
