"""Umumiy konstantalar: kategoriya emojilari, takrorlanish turlari, cheklovlar."""

CATEGORY_EMOJI: dict[str, str] = {
    "meeting": "🤝",
    "medicine": "💊",
    "task": "✅",
    "plan": "🎯",
    "other": "🔔",
    "timer": "⏱",
}
USER_CATEGORIES = ("meeting", "medicine", "task", "plan", "other")
REPEAT_TYPES = ("none", "daily", "weekly", "monthly", "weekdays", "yearly", "interval")

INTERVAL_HOURS = (2, 3, 4, 6, 8, 12)
TIMER_PRESETS = (5, 10, 15, 30, 45, 60, 120)  # daqiqalarda
SNOOZE_MINUTES = (10, 30, 60)

MAX_TEXT_LEN = 500
MAX_ACTIVE_PER_USER = 200
MAX_ACTIVE_PER_CHAT = 100
MAX_TIMER_MINUTES = 24 * 60
MIN_LEAD_SECONDS = 5
PAGE_SIZE = 5
