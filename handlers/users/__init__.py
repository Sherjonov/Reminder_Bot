from aiogram import Router

from . import expenses, fallback, fired, menu, my_reminders, new_reminder, preferences, quick_add, start, timer


def setup_user_router() -> Router:
    """Tartib muhim: avval buyruq/menyu, keyin suhbat bosqichlari, eng oxirida fallback."""
    router = Router(name="users")
    router.include_routers(
        menu.router,
        start.router,
        new_reminder.router,
        my_reminders.router,
        timer.router,
        expenses.router,
        preferences.router,
        fired.router,
        quick_add.router,
        fallback.router,
    )
    return router
