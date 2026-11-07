"""Eslatmalar, taymer, guruh va kartochka matnlari. Tartib: (uz, ru, en)."""

MESSAGES: dict[str, tuple[str, str, str]] = {
    # ------------------------------------------------------------ kategoriyalar va takrorlanish nomlari
    "cat_meeting": ("Uchrashuv", "Встреча", "Meeting"),
    "cat_medicine": ("Dori", "Лекарство", "Medicine"),
    "cat_task": ("Vazifa", "Задача", "Task"),
    "cat_plan": ("Shaxsiy reja", "Личный план", "Personal plan"),
    "cat_other": ("Boshqa", "Другое", "Other"),
    "cat_timer": ("Taymer", "Таймер", "Timer"),
    "rep_none": ("Bir marta", "Один раз", "Once"),
    "rep_daily": ("Har kuni", "Каждый день", "Every day"),
    "rep_weekly": ("Har hafta", "Каждую неделю", "Every week"),
    "rep_monthly": ("Har oy", "Каждый месяц", "Every month"),
    "rep_yearly": ("Har yili", "Каждый год", "Every year"),
    "rep_weekdays": ("Ish kunlari (Du–Ju)", "По будням (Пн–Пт)", "Weekdays (Mon–Fri)"),
    "rb_weekdays": ("Ish kunlari", "По будням", "Weekdays"),
    "rep_interval_h": ("Har {n} soatda", "Каждые {n} ч", "Every {n} hours"),
    "rep_interval_m": ("Har {n} daqiqada", "Каждые {n} мин", "Every {n} minutes"),
    "rb_interval": ("💊 Har N soatda", "💊 Каждые N часов", "💊 Every N hours"),
    "interval_btn": ("{n} soat", "{n} ч", "{n} h"),
    "interval_title": (
        "💊 <b>Necha soatda bir takrorlansin?</b>\n\nBirinchi eslatma tanlangan vaqtda keladi, keyingilari shu oraliqda.",
        "💊 <b>Как часто повторять (в часах)?</b>\n\nПервое напоминание придёт в выбранное время, следующие — через этот интервал.",
        "💊 <b>Repeat every how many hours?</b>\n\nThe first reminder arrives at the chosen time, the next ones at this interval.",
    ),

    # ------------------------------------------------------------ sana va davomiylik so'zlari
    "d_today": ("Bugun", "Сегодня", "Today"),
    "d_tomorrow": ("Ertaga", "Завтра", "Tomorrow"),
    "in_fmt": ("{dur}dan keyin", "через {dur}", "in {dur}"),
    "in_lt_min": ("bir daqiqadan kam vaqtdan keyin", "меньше чем через минуту", "in less than a minute"),

    # ------------------------------------------------------------ kartochka, ro'yxat satrlari
    "card_when": ("🕒 {when}", "🕒 {when}", "🕒 {when}"),
    "card_repeat": ("🔁 {repeat}", "🔁 {repeat}", "🔁 {repeat}"),
    "card_timer_dur": ("⏳ {dur}", "⏳ {dur}", "⏳ {dur}"),
    "card_timer_end": ("🏁 Tugash vaqti: <b>{when}</b>", "🏁 Закончится: <b>{when}</b>", "🏁 Ends at: <b>{when}</b>"),
    "item_timer": (
        "<b>{i}.</b> {emoji} Taymer — {dur} (<b>{clock}</b> da tugaydi)",
        "<b>{i}.</b> {emoji} Таймер — {dur} (закончится в <b>{clock}</b>)",
        "<b>{i}.</b> {emoji} Timer — {dur} (ends at <b>{clock}</b>)",
    ),
    "item_line": (
        "<b>{i}.</b> {emoji} {text}\n      🕒 <b>{when}</b>{rep}",
        "<b>{i}.</b> {emoji} {text}\n      🕒 <b>{when}</b>{rep}",
        "<b>{i}.</b> {emoji} {text}\n      🕒 <b>{when}</b>{rep}",
    ),

    # ------------------------------------------------------------ eslatma vaqti kelganda
    "fired_title": ("🔔 <b>Eslatma!</b>", "🔔 <b>Напоминание!</b>", "🔔 <b>Reminder!</b>"),
    "fired_late": (
        "⌛ <i>Kechikib yetkazildi ({dur} kech)</i>",
        "⌛ <i>Доставлено с опозданием на {dur}</i>",
        "⌛ <i>Delivered late ({dur} late)</i>",
    ),
    "fired_timer": ("⏱ <b>Taymer tugadi!</b>", "⏱ <b>Таймер закончился!</b>", "⏱ <b>Timer finished!</b>"),
    "fired_timer_body": ("{dur} o'tdi.", "Прошло {dur}.", "{dur} have passed."),
    "btn_done": ("✅ Bajarildi", "✅ Выполнено", "✅ Done"),
    "btn_snooze_m": ("⏰ {m} daq", "⏰ {m} мин", "⏰ {m} min"),
    "btn_snooze_h": ("⏰ {h} soat", "⏰ {h} ч", "⏰ {h} h"),
    "btn_timer_again": ("🔁 Yana {dur}", "🔁 Ещё {dur}", "🔁 Again {dur}"),
    "btn_ok": ("✅ OK", "✅ OK", "✅ OK"),
    "done_mark": ("✅ <b>Bajarildi</b>", "✅ <b>Выполнено</b>", "✅ <b>Done</b>"),
    "snoozed_mark": (
        "⏰ <b>{dur}ga kechiktirildi</b> — soat {clock} da qayta eslataman",
        "⏰ <b>Отложено на {dur}</b> — напомню снова в {clock}",
        "⏰ <b>Snoozed for {dur}</b> — I'll remind you again at {clock}",
    ),
    "done_toast": ("Barakalla! ✅", "Отлично! ✅", "Well done! ✅"),
    "snoozed_toast": ("⏰ Kechiktirildi", "⏰ Отложено", "⏰ Snoozed"),
    "timer_again_toast": ("⏱ Taymer qayta ishga tushdi", "⏱ Таймер запущен снова", "⏱ Timer restarted"),
    "digest_title": ("🌅 <b>Xayrli tong!</b>", "🌅 <b>Доброе утро!</b>", "🌅 <b>Good morning!</b>"),
    "digest_header": (
        "Bugungi eslatmalaringiz ({n} ta):",
        "Ваши напоминания на сегодня ({n}):",
        "Your reminders for today ({n}):",
    ),
    "digest_footer": ("Kuningiz barakali o'tsin! ✨", "Хорошего дня! ✨", "Have a great day! ✨"),

    # ------------------------------------------------------------ yangi eslatma
    "nr_title": (
        "📝 <b>Yangi eslatma</b>\n\nQaysi turdagi eslatma qo'shamiz?",
        "📝 <b>Новое напоминание</b>\n\nКакого типа напоминание добавим?",
        "📝 <b>New reminder</b>\n\nWhat kind of reminder shall we add?",
    ),
    "nr_ask_text": (
        "{emoji} <b>{name}</b>\n\nNimani eslatay? Matnni yozib yuboring.\n<i>Masalan: Shifokor qabuliga borish</i>",
        "{emoji} <b>{name}</b>\n\nО чём напомнить? Напишите текст.\n<i>Например: Сходить на приём к врачу</i>",
        "{emoji} <b>{name}</b>\n\nWhat should I remind you about? Send the text.\n<i>For example: Go to the doctor's appointment</i>",
    ),
    "nr_text_short": (
        "✍️ Matn juda qisqa. Iltimos, batafsilroq yozing.",
        "✍️ Текст слишком короткий. Напишите подробнее.",
        "✍️ The text is too short. Please be more specific.",
    ),
    "nr_text_long": (
        "✂️ Matn juda uzun ({n} belgi). {max} belgigacha qisqartiring.",
        "✂️ Текст слишком длинный ({n} символов). Сократите до {max}.",
        "✂️ The text is too long ({n} characters). Shorten it to {max}.",
    ),
    "nr_text_range": (
        "✍️ Matn 2 dan {max} belgigacha bo'lishi kerak.",
        "✍️ Текст должен содержать от 2 до {max} символов.",
        "✍️ The text must be between 2 and {max} characters.",
    ),
    "when_prompt": (
        "🕒 <b>Qachon eslatay?</b>\n\n"
        "Pastdagi tugmalardan tanlang yoki vaqtni o'zingiz yozing:\n"
        "• <code>bugun 18:30</code>\n• <code>ertaga soat 9 da</code>\n• <code>30 daqiqadan keyin</code>\n"
        "• <code>dushanba 10:00</code>\n• <code>25.12 14:00</code>",
        "🕒 <b>Когда напомнить?</b>\n\n"
        "Выберите кнопку ниже или напишите время сами:\n"
        "• <code>сегодня в 18:30</code>\n• <code>завтра в 9 утра</code>\n• <code>через 30 минут</code>\n"
        "• <code>в понедельник в 10:00</code>\n• <code>25.12 14:00</code>",
        "🕒 <b>When should I remind you?</b>\n\n"
        "Pick a button below or write the time yourself:\n"
        "• <code>today 18:30</code>\n• <code>tomorrow at 9am</code>\n• <code>in 30 minutes</code>\n"
        "• <code>monday 10:00</code>\n• <code>25.12 14:00</code>",
    ),
    "not_understood": (
        "🤔 Vaqtni tushunmadim. Quyidagicha yozib ko'ring:\n• <code>bugun 18:30</code>\n"
        "• <code>ertaga soat 9 da</code>\n• <code>2 soatdan keyin</code>\n• <code>25.12 14:00</code>\n\n"
        "<i>Soatni ikki nuqta bilan yozing, masalan: 9:30</i>",
        "🤔 Не понял время. Попробуйте так:\n• <code>сегодня в 18:30</code>\n"
        "• <code>завтра в 9 утра</code>\n• <code>через 2 часа</code>\n• <code>25.12 14:00</code>\n\n"
        "<i>Часы пишите через двоеточие, например: 9:30</i>",
        "🤔 I couldn't understand the time. Try like this:\n• <code>today 18:30</code>\n"
        "• <code>tomorrow at 9am</code>\n• <code>in 2 hours</code>\n• <code>25.12 14:00</code>\n\n"
        "<i>Write hours with a colon, e.g. 9:30</i>",
    ),
    "past_time": (
        "⏳ Bu vaqt allaqachon o'tib ketgan. Iltimos, kelajakdagi vaqtni yozing.",
        "⏳ Это время уже прошло. Напишите время в будущем.",
        "⏳ That time has already passed. Please write a time in the future.",
    ),
    "qt_m10": ("⏱ 10 daqiqadan keyin", "⏱ Через 10 минут", "⏱ In 10 minutes"),
    "qt_m30": ("⏱ 30 daqiqadan keyin", "⏱ Через 30 минут", "⏱ In 30 minutes"),
    "qt_h1": ("⏱ 1 soatdan keyin", "⏱ Через 1 час", "⏱ In 1 hour"),
    "qt_eve": ("🌆 Bugun 20:00", "🌆 Сегодня 20:00", "🌆 Today 20:00"),
    "qt_tom": ("🌅 Ertaga 09:00", "🌅 Завтра 09:00", "🌅 Tomorrow 09:00"),
    "cf_card": (
        "📝 <b>Eslatmani tasdiqlang</b>\n\n{emoji} <b>{name}</b>\n{text}\n\n🕒 <b>{when}</b>\n⏳ {in_}\n🔁 {repeat}{note}\n\n"
        "<i>Takrorlanishni tanlang yoki saqlang 👇</i>",
        "📝 <b>Подтвердите напоминание</b>\n\n{emoji} <b>{name}</b>\n{text}\n\n🕒 <b>{when}</b>\n⏳ {in_}\n🔁 {repeat}{note}\n\n"
        "<i>Выберите повторение или сохраните 👇</i>",
        "📝 <b>Confirm the reminder</b>\n\n{emoji} <b>{name}</b>\n{text}\n\n🕒 <b>{when}</b>\n⏳ {in_}\n🔁 {repeat}{note}\n\n"
        "<i>Choose a repeat option or save 👇</i>",
    ),
    "cf_assumed": (
        "\n\n<i>⚠️ Soat ko'rsatilmagani uchun 09:00 qo'yildi. Kerak bo'lsa «Vaqtni o'zgartirish» ni bosing.</i>",
        "\n\n<i>⚠️ Время не указано, поэтому выставлено 09:00. При необходимости нажмите «Изменить время».</i>",
        "\n\n<i>⚠️ No time was given, so 09:00 was set. Press “Change time” if needed.</i>",
    ),
    "btn_change_time": ("🕒 Vaqtni o'zgartirish", "🕒 Изменить время", "🕒 Change time"),
    "btn_text": ("✏️ Matn", "✏️ Текст", "✏️ Text"),
    "edit_text_prompt": (
        "✏️ <b>Yangi matnni yozing</b>\n\nHozirgi matn:\n<i>{text}</i>",
        "✏️ <b>Напишите новый текст</b>\n\nТекущий текст:\n<i>{text}</i>",
        "✏️ <b>Write the new text</b>\n\nCurrent text:\n<i>{text}</i>",
    ),
    "confirm_hint": (
        "👆 Tugmalardan foydalaning yoki yangi vaqtni yozing (masalan: <code>ertaga 9:00</code>).",
        "👆 Используйте кнопки или напишите новое время (например: <code>завтра 9:00</code>).",
        "👆 Use the buttons or write a new time (e.g. <code>tomorrow 9:00</code>).",
    ),
    "time_passed_alert": (
        "⏳ Bu vaqt o'tib ketdi. «Vaqtni o'zgartirish» ni bosing.",
        "⏳ Это время прошло. Нажмите «Изменить время».",
        "⏳ That time has passed. Press “Change time”.",
    ),
    "limit_reached": (
        "Faol eslatmalar soni {max} tadan oshmasligi kerak. Eskilarini o'chiring.",
        "Количество активных напоминаний не должно превышать {max}. Удалите старые.",
        "The number of active reminders must not exceed {max}. Delete old ones.",
    ),
    "saved_title": ("✅ <b>Eslatma saqlandi!</b>", "✅ <b>Напоминание сохранено!</b>", "✅ <b>Reminder saved!</b>"),
    "saved_in": ("{in_} eslataman.", "Напомню {in_}.", "I'll remind you {in_}."),
    "saved_toast": ("Saqlandi ✅", "Сохранено ✅", "Saved ✅"),
    "qa_no_text": (
        "🤔 Vaqtni tushundim, lekin <b>nimani eslatish</b> kerakligini topa olmadim.\n"
        "Masalan: <i>ertaga 9:00 da shifokorga borish</i>\n\nYoki «➕ Yangi eslatma» tugmasidan foydalaning.",
        "🤔 Время понял, но не нашёл, <b>о чём напомнить</b>.\n"
        "Например: <i>завтра в 9:00 сходить к врачу</i>\n\nИли воспользуйтесь кнопкой «➕ Новое напоминание».",
        "🤔 I got the time but couldn't find <b>what to remind you about</b>.\n"
        "For example: <i>tomorrow at 9:00 see the doctor</i>\n\nOr use the “➕ New reminder” button.",
    ),

    # ------------------------------------------------------------ ro'yxat, tafsilot, tahrirlash
    "list_title_all": ("📋 <b>Faol eslatmalarim</b>", "📋 <b>Мои активные напоминания</b>", "📋 <b>My active reminders</b>"),
    "list_title_today": ("📅 <b>Bugungi eslatmalar</b>", "📅 <b>Напоминания на сегодня</b>", "📅 <b>Today's reminders</b>"),
    "list_count": ("{title} — {total} ta", "{title} — {total}", "{title} — {total}"),
    "list_empty_all": ("Hozircha faol eslatmalar yo'q.", "Активных напоминаний пока нет.", "No active reminders yet."),
    "list_empty_today": ("Bugun uchun eslatmalar yo'q 🎉", "На сегодня напоминаний нет 🎉", "No reminders for today 🎉"),
    "list_empty_hint": (
        "Yangi eslatma qo'shish uchun pastdagi tugmani bosing 👇",
        "Чтобы добавить напоминание, нажмите кнопку ниже 👇",
        "Press the button below to add a new reminder 👇",
    ),
    "list_page": ("Sahifa {p}/{n}", "Страница {p}/{n}", "Page {p}/{n}"),
    "list_open_hint": (
        "Batafsil ko'rish uchun raqamni bosing.",
        "Нажмите на номер, чтобы открыть подробности.",
        "Press a number to see the details.",
    ),
    "btn_edit_text": ("✏️ Matn", "✏️ Текст", "✏️ Text"),
    "btn_edit_time": ("🕒 Vaqt", "🕒 Время", "🕒 Time"),
    "btn_delete": ("🗑 O'chirish", "🗑 Удалить", "🗑 Delete"),
    "btn_to_list": ("⬅️ Ro'yxatga", "⬅️ К списку", "⬅️ To the list"),
    "btn_del_yes": ("🗑 Ha, o'chirish", "🗑 Да, удалить", "🗑 Yes, delete"),
    "del_confirm": (
        "🗑 <b>O'chirishni tasdiqlaysizmi?</b>\n\n{card}",
        "🗑 <b>Подтвердить удаление?</b>\n\n{card}",
        "🗑 <b>Confirm deletion?</b>\n\n{card}",
    ),
    "deleted_toast": ("🗑 O'chirildi", "🗑 Удалено", "🗑 Deleted"),
    "text_updated": (
        "✅ <b>Matn yangilandi</b>\n\n{card}",
        "✅ <b>Текст обновлён</b>\n\n{card}",
        "✅ <b>Text updated</b>\n\n{card}",
    ),
    "time_updated": (
        "✅ <b>Vaqt yangilandi</b>\n\n{card}",
        "✅ <b>Время обновлено</b>\n\n{card}",
        "✅ <b>Time updated</b>\n\n{card}",
    ),
    "edit_time_prompt": (
        "🕒 <b>Yangi vaqtni yozing</b>\n\nMasalan: <code>bugun 18:30</code>, <code>ertaga soat 9 da</code>, "
        "<code>2 soatdan keyin</code>, <code>25.12 14:00</code>",
        "🕒 <b>Напишите новое время</b>\n\nНапример: <code>сегодня в 18:30</code>, <code>завтра в 9 утра</code>, "
        "<code>через 2 часа</code>, <code>25.12 14:00</code>",
        "🕒 <b>Write the new time</b>\n\nFor example: <code>today 18:30</code>, <code>tomorrow at 9am</code>, "
        "<code>in 2 hours</code>, <code>25.12 14:00</code>",
    ),
    "rem_gone": (
        "Bu eslatma topilmadi (o'chirilgan yoki allaqachon yuborilgan).",
        "Напоминание не найдено (удалено или уже отправлено).",
        "This reminder was not found (deleted or already sent).",
    ),
    "rem_nf": ("Bu eslatma topilmadi.", "Напоминание не найдено.", "Reminder not found."),
    "rem_nf_short": ("Eslatma topilmadi.", "Напоминание не найдено.", "Reminder not found."),

    # ------------------------------------------------------------ taymer
    "timer_menu": (
        "⏱ <b>Taymer</b>\n\nQancha vaqt sanaymiz? Vaqt tugagach sizga xabar beraman.\n\n"
        "Tayyor vaqtni tanlang yoki <b>✍️ Boshqa vaqt</b> tugmasini bosing.",
        "⏱ <b>Таймер</b>\n\nСколько отсчитываем? Когда время выйдет, я сообщу.\n\n"
        "Выберите готовое время или нажмите <b>✍️ Другое время</b>.",
        "⏱ <b>Timer</b>\n\nHow long shall we count? I'll let you know when time is up.\n\n"
        "Pick a preset or press <b>✍️ Custom time</b>.",
    ),
    "timer_custom": (
        "✍️ <b>Taymer vaqtini yozing</b>\n\n• <code>25</code> — 25 daqiqa\n• <code>1:30</code> — 1 soat 30 daqiqa\n"
        "• <code>2 soat</code>, <code>45 daqiqa</code>, <code>yarim soat</code>\n\n<i>Eng ko'pi bilan 24 soat.</i>",
        "✍️ <b>Напишите время таймера</b>\n\n• <code>25</code> — 25 минут\n• <code>1:30</code> — 1 час 30 минут\n"
        "• <code>2 часа</code>, <code>45 минут</code>, <code>полчаса</code>\n\n<i>Не более 24 часов.</i>",
        "✍️ <b>Write the timer duration</b>\n\n• <code>25</code> — 25 minutes\n• <code>1:30</code> — 1 hour 30 minutes\n"
        "• <code>2 hours</code>, <code>45 minutes</code>, <code>half an hour</code>\n\n<i>24 hours at most.</i>",
    ),
    "timer_started": (
        "⏱ <b>Taymer ishga tushdi!</b>\n\n⏳ Davomiyligi: <b>{dur}</b>\n🏁 Tugash vaqti: <b>{when}</b>\n\n"
        "Vaqt tugagach sizga xabar beraman.",
        "⏱ <b>Таймер запущен!</b>\n\n⏳ Длительность: <b>{dur}</b>\n🏁 Закончится: <b>{when}</b>\n\n"
        "Когда время выйдет, я сообщу.",
        "⏱ <b>Timer started!</b>\n\n⏳ Duration: <b>{dur}</b>\n🏁 Ends at: <b>{when}</b>\n\n"
        "I'll let you know when time is up.",
    ),
    "timer_cancelled": ("🛑 <b>Taymer bekor qilindi.</b>", "🛑 <b>Таймер отменён.</b>", "🛑 <b>Timer cancelled.</b>"),
    "timer_bad": (
        "🤔 Vaqtni tushunmadim. Masalan: <code>25</code> (daqiqa), <code>1:30</code>, <code>2 soat</code> yoki <code>45 daqiqa</code>.",
        "🤔 Не понял время. Например: <code>25</code> (минут), <code>1:30</code>, <code>2 часа</code> или <code>45 минут</code>.",
        "🤔 I couldn't understand the time. For example: <code>25</code> (minutes), <code>1:30</code>, <code>2 hours</code> or <code>45 minutes</code>.",
    ),
    "timer_too_long": (
        "⏳ Taymer 24 soatdan oshmasligi kerak. Uzoqroq vaqt uchun «➕ Yangi eslatma» dan foydalaning.",
        "⏳ Таймер не может быть больше 24 часов. Для более долгого срока используйте «➕ Новое напоминание».",
        "⏳ A timer can't exceed 24 hours. For longer periods use “➕ New reminder”.",
    ),
    "btn_custom_time": ("✍️ Boshqa vaqt", "✍️ Другое время", "✍️ Custom time"),
    "btn_timer_stop": ("🛑 Bekor qilish", "🛑 Отменить", "🛑 Cancel"),
    "timer_toast": ("⏱ Taymer ishga tushdi", "⏱ Таймер запущен", "⏱ Timer started"),
    "timer_h": ("{n} soat", "{n} ч", "{n} h"),

    # ------------------------------------------------------------ guruhlar
    "g_help": (
        "👋 Men guruhda ham eslatma o'rnata olaman.\n\n"
        "<b>/eslat</b> <i>vaqt matn</i> — guruhga eslatma qo'shish\n"
        "Masalan: <code>/eslat ertaga 9:00 yig'ilish</code>\n"
        "yoki: <code>/eslat 30 daqiqadan keyin chiqish</code>\n\n"
        "<b>/eslatmalar</b> — guruhning faol eslatmalari\n\n"
        "🕒 Vaqt sizning sozlamangizdagi vaqt mintaqasi bo'yicha olinadi (shaxsiy chatda ⚙️ Sozlamalar).",
        "👋 Я могу ставить напоминания и в группе.\n\n"
        "<b>/eslat</b> <i>время текст</i> — добавить напоминание в группу\n"
        "Например: <code>/eslat завтра 9:00 совещание</code>\n"
        "или: <code>/eslat через 30 минут выходим</code>\n\n"
        "<b>/eslatmalar</b> — активные напоминания группы\n\n"
        "🕒 Время берётся по часовому поясу из ваших настроек (в личном чате ⚙️ Настройки).",
        "👋 I can set reminders in groups too.\n\n"
        "<b>/eslat</b> <i>time text</i> — add a reminder to the group\n"
        "For example: <code>/eslat tomorrow 9:00 meeting</code>\n"
        "or: <code>/eslat in 30 minutes let's go</code>\n\n"
        "<b>/eslatmalar</b> — the group's active reminders\n\n"
        "🕒 The time uses the time zone from your settings (⚙️ Settings in a private chat).",
    ),
    "g_anon": (
        "Anonim rejimda eslatma qo'sha olmayman. Iltimos, o'z nomingizdan yozing.",
        "В анонимном режиме я не могу добавить напоминание. Пишите, пожалуйста, от своего имени.",
        "I can't add reminders in anonymous mode. Please write from your own account.",
    ),
    "g_bad": (
        "🤔 Vaqt va matnni tushunmadim.\nMasalan: <code>/eslat ertaga 9:00 yig'ilish</code>",
        "🤔 Не понял время и текст.\nНапример: <code>/eslat завтра 9:00 совещание</code>",
        "🤔 I couldn't understand the time and text.\nFor example: <code>/eslat tomorrow 9:00 meeting</code>",
    ),
    "g_long": (
        "✂️ Matn juda uzun. {max} belgigacha yozing.",
        "✂️ Текст слишком длинный. Не более {max} символов.",
        "✂️ The text is too long. Up to {max} characters.",
    ),
    "g_past": ("⏳ Bu vaqt allaqachon o'tib ketgan.", "⏳ Это время уже прошло.", "⏳ That time has already passed."),
    "g_limit": (
        "Bu guruhda faol eslatmalar {max} tadan oshmasligi kerak.",
        "В этой группе не может быть больше {max} активных напоминаний.",
        "A group can have at most {max} active reminders.",
    ),
    "g_saved": (
        "✅ <b>Guruh eslatmasi saqlandi</b> (#{id})\n\n🔔 {text}\n🕒 {when}\n⏳ {in_} eslataman.",
        "✅ <b>Напоминание для группы сохранено</b> (#{id})\n\n🔔 {text}\n🕒 {when}\n⏳ Напомню {in_}.",
        "✅ <b>Group reminder saved</b> (#{id})\n\n🔔 {text}\n🕒 {when}\n⏳ I'll remind {in_}.",
    ),
    "g_empty": (
        "📭 Bu guruhda faol eslatmalar yo'q.\n\nQo'shish: <code>/eslat ertaga 9:00 yig'ilish</code>",
        "📭 В этой группе нет активных напоминаний.\n\nДобавить: <code>/eslat завтра 9:00 совещание</code>",
        "📭 This group has no active reminders.\n\nAdd one: <code>/eslat tomorrow 9:00 meeting</code>",
    ),
    "g_list_title": (
        "📋 <b>Guruh eslatmalari</b> ({n} ta)",
        "📋 <b>Напоминания группы</b> ({n})",
        "📋 <b>Group reminders</b> ({n})",
    ),
    "g_list_hint": (
        "<i>O'chirish uchun tugmani bosing (eslatma egasi yoki guruh admini).</i>",
        "<i>Для удаления нажмите кнопку (автор напоминания или админ группы).</i>",
        "<i>Press a button to delete (the author or a group admin).</i>",
    ),
    "g_forbidden": (
        "Faqat eslatma egasi yoki guruh admini o'chira oladi.",
        "Удалить может только автор напоминания или админ группы.",
        "Only the author or a group admin can delete it.",
    ),
}
