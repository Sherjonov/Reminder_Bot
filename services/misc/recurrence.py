"""Takrorlanuvchi eslatmaning keyingi vaqtini hisoblash."""
from __future__ import annotations

from datetime import datetime, timedelta

from .timeutils import add_months, get_tz, to_local, to_utc


def next_occurrence(
    remind_at: datetime,
    repeat_type: str,
    repeat_value: int | None,
    tz_name: str,
    after: datetime,
) -> datetime | None:
    """`remind_at` (UTC) dan keyingi, `after` dan katta bo'lgan vaqtni (UTC) qaytaradi.

    Kunlik/haftalik/oylik takrorlar mahalliy "devor soati" bo'yicha suriladi, shuning uchun
    yozgi/qishki vaqtga o'tiladigan mintaqalarda ham eslatma bir xil soatda keladi.
    """
    if repeat_type in (None, "", "none"):
        return None

    if repeat_type == "interval":
        step = timedelta(minutes=max(int(repeat_value or 60), 1))
        if remind_at > after:
            return remind_at
        steps = int((after - remind_at) / step) + 1
        return remind_at + step * steps

    tz = get_tz(tz_name)
    local = to_local(remind_at, tz)
    for _ in range(4000):
        if repeat_type == "daily":
            local = local + timedelta(days=1)
        elif repeat_type == "weekly":
            local = local + timedelta(days=7)
        elif repeat_type == "weekdays":
            local = local + timedelta(days=1)
            while local.weekday() >= 5:
                local = local + timedelta(days=1)
        elif repeat_type == "monthly":
            local = add_months(local, 1, repeat_value)
        elif repeat_type == "yearly":
            local = add_months(local, 12)
        else:
            return None
        candidate = to_utc(local)
        if candidate > after:
            return candidate
    return None
