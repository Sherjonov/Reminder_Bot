"""Sozlamalar, vaqt mintaqasi, soatni moslash. Tartib: (uz, ru, en)."""

MESSAGES: dict[str, tuple[str, str, str]] = {
    "set_text": (
        "⚙️ <b>Sozlamalar</b>\n\n"
        "🌍 Vaqt mintaqasi: <b>{tz}</b>\n"
        "🕒 Hozirgi vaqtingiz: <b>{now}</b>\n"
        "🌅 Kunlik xulosa: <b>{digest}</b>\n"
        "🌐 Til: <b>{language}</b>\n\n"
        "<i>Eslatmalar shu mintaqa vaqti bo'yicha o'rnatiladi. Kunlik xulosa — ertalab bugungi eslatmalar ro'yxati.</i>",
        "⚙️ <b>Настройки</b>\n\n"
        "🌍 Часовой пояс: <b>{tz}</b>\n"
        "🕒 Ваше время сейчас: <b>{now}</b>\n"
        "🌅 Ежедневная сводка: <b>{digest}</b>\n"
        "🌐 Язык: <b>{language}</b>\n\n"
        "<i>Напоминания ставятся по времени этого пояса. Ежедневная сводка — список напоминаний на сегодня утром.</i>",
        "⚙️ <b>Settings</b>\n\n"
        "🌍 Time zone: <b>{tz}</b>\n"
        "🕒 Your time now: <b>{now}</b>\n"
        "🌅 Daily digest: <b>{digest}</b>\n"
        "🌐 Language: <b>{language}</b>\n\n"
        "<i>Reminders are set in this time zone. The daily digest is the list of today's reminders in the morning.</i>",
    ),
    "set_digest_on": (
        "yoqilgan ✅ (har kuni {hour}:00 da)",
        "включена ✅ (каждый день в {hour}:00)",
        "on ✅ (every day at {hour}:00)",
    ),
    "set_digest_off": ("o'chiq", "выключена", "off"),
    "sb_tz": ("🌍 Vaqt mintaqasini o'zgartirish", "🌍 Изменить часовой пояс", "🌍 Change time zone"),
    "sb_digest_on": ("🌅 Kunlik xulosa: yoqilgan ✅", "🌅 Ежедневная сводка: включена ✅", "🌅 Daily digest: on ✅"),
    "sb_digest_off": ("🌅 Kunlik xulosa: o'chiq", "🌅 Ежедневная сводка: выключена", "🌅 Daily digest: off"),
    "sb_clock": ("🕒 Soatim noto'g'ri — moslash", "🕒 Неверное время — настроить", "🕒 Wrong time — adjust"),
    "sb_lang": ("🌐 Til / Язык / Language", "🌐 Til / Язык / Language", "🌐 Til / Язык / Language"),
    "sb_wipe": ("🗑 Ma'lumotlarimni o'chirish", "🗑 Удалить мои данные", "🗑 Delete my data"),
    "lang_pick": (
        "🌐 <b>Tilni tanlang</b>\n\nBot siz yozgan tilga ham o'zi moslashadi.",
        "🌐 <b>Выберите язык</b>\n\nБот также подстраивается под язык, на котором вы пишете.",
        "🌐 <b>Choose a language</b>\n\nThe bot also adapts to the language you write in.",
    ),
    "tz_pick": (
        "🌍 <b>Vaqt mintaqangizni tanlang</b>\n\nEslatmalar shu mintaqa vaqti bo'yicha o'rnatiladi.",
        "🌍 <b>Выберите часовой пояс</b>\n\nНапоминания ставятся по времени этого пояса.",
        "🌍 <b>Choose your time zone</b>\n\nReminders are set in this time zone.",
    ),
    "tz_custom_btn": ("✍️ Boshqa mintaqa", "✍️ Другой пояс", "✍️ Other zone"),
    "tz_custom_prompt": (
        "✍️ <b>Vaqt mintaqasini yozing</b>\n\n• <code>+5</code> yoki <code>UTC+3</code>\n"
        "• <code>Asia/Tokyo</code>, <code>Europe/London</code>\n• yoki shahar nomi: <code>Moskva</code>, <code>Seul</code>",
        "✍️ <b>Напишите часовой пояс</b>\n\n• <code>+5</code> или <code>UTC+3</code>\n"
        "• <code>Asia/Tokyo</code>, <code>Europe/London</code>\n• или город: <code>Москва</code>, <code>Сеул</code>",
        "✍️ <b>Write the time zone</b>\n\n• <code>+5</code> or <code>UTC+3</code>\n"
        "• <code>Asia/Tokyo</code>, <code>Europe/London</code>\n• or a city: <code>Moscow</code>, <code>Seoul</code>",
    ),
    "tz_bad": (
        "🤔 Bunday vaqt mintaqasi topilmadi. Masalan: <code>+5</code>, <code>UTC+3</code> yoki <code>Asia/Tokyo</code>.",
        "🤔 Такой часовой пояс не найден. Например: <code>+5</code>, <code>UTC+3</code> или <code>Asia/Tokyo</code>.",
        "🤔 That time zone wasn't found. For example: <code>+5</code>, <code>UTC+3</code> or <code>Asia/Tokyo</code>.",
    ),
    "tz_changed": (
        "✅ Vaqt mintaqasi o'zgardi: <b>{tz}</b>",
        "✅ Часовой пояс изменён: <b>{tz}</b>",
        "✅ Time zone changed: <b>{tz}</b>",
    ),
    "digest_toast_on": ("🌅 Kunlik xulosa yoqildi", "🌅 Ежедневная сводка включена", "🌅 Daily digest turned on"),
    "digest_toast_off": ("Kunlik xulosa o'chirildi", "Ежедневная сводка выключена", "Daily digest turned off"),
    "clock_prompt": (
        "🕒 <b>Soatni moslash</b>\n\nHozir telefoningizdagi (haqiqiy) vaqtni yozing, masalan: <code>14:25</code>.\n"
        "Bot vaqt mintaqasini shunga moslab qo'yadi.\n\nHozir bot hisobida: <b>{now}</b> ({tz})",
        "🕒 <b>Настройка времени</b>\n\nНапишите, сколько сейчас на вашем телефоне (реальное время), например: <code>14:25</code>.\n"
        "Бот подберёт часовой пояс.\n\nСейчас у бота: <b>{now}</b> ({tz})",
        "🕒 <b>Adjust the time</b>\n\nWrite the current real time on your phone, e.g. <code>14:25</code>.\n"
        "The bot will pick the matching time zone.\n\nThe bot currently thinks: <b>{now}</b> ({tz})",
    ),
    "clock_bad": (
        "🤔 Soatni tushunmadim. Masalan: <code>14:25</code> yoki <code>2:37 pm</code>.",
        "🤔 Не понял время. Например: <code>14:25</code> или <code>2:37 pm</code>.",
        "🤔 I couldn't understand the time. For example: <code>14:25</code> or <code>2:37 pm</code>.",
    ),
    "clock_done": (
        "✅ Vaqt moslandi: <b>{tz}</b>\n🕒 Hozir: <b>{now}</b>",
        "✅ Время настроено: <b>{tz}</b>\n🕒 Сейчас: <b>{now}</b>",
        "✅ Time adjusted: <b>{tz}</b>\n🕒 Now: <b>{now}</b>",
    ),
    "clock_same": (
        "✅ Soat to'g'ri ko'rinadi: <b>{now}</b> ({tz})",
        "✅ Время выглядит верным: <b>{now}</b> ({tz})",
        "✅ The time looks right: <b>{now}</b> ({tz})",
    ),
    "clock_nozone": (
        "🤔 Bu soatga mos vaqt mintaqasi topilmadi. Vaqt mintaqasini ro'yxatdan tanlang.",
        "🤔 Не удалось подобрать часовой пояс. Выберите его из списка.",
        "🤔 No matching time zone was found. Please choose one from the list.",
    ),
    "wipe_ask": (
        "🗑 <b>Barcha ma'lumotlaringiz o'chirilsinmi?</b>\n\n"
        "Barcha eslatma, taymer va xarajatlaringiz butunlay o'chadi. Buni qaytarib bo'lmaydi.",
        "🗑 <b>Удалить все ваши данные?</b>\n\n"
        "Все напоминания, таймеры и расходы будут удалены безвозвратно.",
        "🗑 <b>Delete all your data?</b>\n\n"
        "All reminders, timers and expenses will be deleted permanently. This cannot be undone.",
    ),
    "btn_wipe_yes": ("🗑 Ha, hammasini o'chir", "🗑 Да, удалить всё", "🗑 Yes, delete everything"),
    "wipe_done": (
        "✅ Barcha ma'lumotlaringiz o'chirildi.\n\nQayta boshlash uchun /start ni bosing.",
        "✅ Все ваши данные удалены.\n\nЧтобы начать заново, нажмите /start.",
        "✅ All your data has been deleted.\n\nPress /start to begin again.",
    ),
    "time_cmd": (
        "🕒 <b>Vaqt</b>\n\nSizning vaqtingiz: <b>{now}</b>\nVaqt mintaqasi: <b>{tz}</b>\n\n"
        "<i>Agar soat noto'g'ri bo'lsa — Sozlamalar → «Soatim noto'g'ri».</i>",
        "🕒 <b>Время</b>\n\nВаше время: <b>{now}</b>\nЧасовой пояс: <b>{tz}</b>\n\n"
        "<i>Если время неверное — Настройки → «Неверное время».</i>",
        "🕒 <b>Time</b>\n\nYour time: <b>{now}</b>\nTime zone: <b>{tz}</b>\n\n"
        "<i>If the time is wrong — Settings → “Wrong time”.</i>",
    ),
    "time_cmd_admin": (
        "\n\n🛠 Kompyuter soati tuzatishi: <b>{offset}</b> (manba: {source})\nUTC (tuzatilgan): <b>{utc}</b>",
        "\n\n🛠 Поправка часов компьютера: <b>{offset}</b> (источник: {source})\nUTC (с поправкой): <b>{utc}</b>",
        "\n\n🛠 Computer clock correction: <b>{offset}</b> (source: {source})\nUTC (corrected): <b>{utc}</b>",
    ),
}
