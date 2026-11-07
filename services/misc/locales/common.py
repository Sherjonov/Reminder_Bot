"""Umumiy matnlar: menyu, xatolar, salomlashuv, yordam, admin paneli. Tartib: (uz, ru, en)."""

MESSAGES: dict[str, tuple[str, str, str]] = {
    # ------------------------------------------------------------ menyu tugmalari ("btn_" — til aniqlashda ishlatiladi)
    "btn_new": ("➕ Yangi eslatma", "➕ Новое напоминание", "➕ New reminder"),
    "btn_timer": ("⏱ Taymer", "⏱ Таймер", "⏱ Timer"),
    "btn_list": ("📋 Eslatmalarim", "📋 Мои напоминания", "📋 My reminders"),
    "btn_today": ("📅 Bugun", "📅 Сегодня", "📅 Today"),
    "btn_expenses": ("💰 Xarajatlar", "💰 Расходы", "💰 Expenses"),
    "btn_settings": ("⚙️ Sozlamalar", "⚙️ Настройки", "⚙️ Settings"),
    "btn_help": ("ℹ️ Yordam", "ℹ️ Помощь", "ℹ️ Help"),
    "placeholder": (
        "Masalan: ertaga 9:00 da dori ichishni eslat",
        "Например: завтра в 9:00 выпить таблетку",
        "E.g. remind me tomorrow at 9:00 to take pills",
    ),
    "t_cancel": ("❌ Bekor qilish", "❌ Отмена", "❌ Cancel"),
    "t_save": ("✅ Saqlash", "✅ Сохранить", "✅ Save"),
    "t_back": ("⬅️ Orqaga", "⬅️ Назад", "⬅️ Back"),
    "t_yes": ("✅ Ha", "✅ Да", "✅ Yes"),
    "t_no": ("↩️ Yo'q", "↩️ Нет", "↩️ No"),

    # ------------------------------------------------------------ umumiy xabarlar
    "lang_changed": ("🌐 Til: <b>O'zbekcha</b>", "🌐 Язык: <b>Русский</b>", "🌐 Language: <b>English</b>"),
    "cancelled": ("❌ Bekor qilindi.", "❌ Отменено.", "❌ Cancelled."),
    "nothing_to_cancel": (
        "Hozir bekor qilinadigan amal yo'q 🙂",
        "Сейчас нечего отменять 🙂",
        "There is nothing to cancel right now 🙂",
    ),
    "throttle": ("⏳ Sekinroq, iltimos 🙂", "⏳ Помедленнее, пожалуйста 🙂", "⏳ Slow down, please 🙂"),
    "err_generic": (
        "😔 Kutilmagan xatolik yuz berdi. Iltimos, qayta urinib ko'ring yoki /bekor ni bosing.",
        "😔 Произошла непредвиденная ошибка. Попробуйте ещё раз или нажмите /bekor.",
        "😔 Something went wrong. Please try again or press /bekor.",
    ),
    "err_alert": (
        "😔 Xatolik yuz berdi. Qayta urinib ko'ring.",
        "😔 Произошла ошибка. Попробуйте ещё раз.",
        "😔 An error occurred. Please try again.",
    ),
    "unknown_cmd": (
        "🤔 Bu buyruqni tanimadim. Yordam uchun /yordam ni bosing.",
        "🤔 Не знаю такой команды. Справка: /yordam.",
        "🤔 I don't know this command. Press /yordam for help.",
    ),
    "unsupported": (
        "📝 Hozircha faqat matn bilan ishlayman.\nMenyudan tanlang yoki shunday yozing: <i>ertaga 9:00 da dori ichishni eslat</i>",
        "📝 Пока я работаю только с текстом.\nВыберите в меню или напишите так: <i>завтра в 9:00 напомни выпить таблетку</i>",
        "📝 For now I only work with text.\nPick from the menu or write like this: <i>remind me tomorrow at 9:00 to take pills</i>",
    ),
    "wrong_in_flow": (
        "✍️ Iltimos, so'ralgan ma'lumotni matn ko'rinishida yuboring yoki /bekor ni bosing.",
        "✍️ Пожалуйста, отправьте запрошенные данные текстом или нажмите /bekor.",
        "✍️ Please send the requested information as text or press /bekor.",
    ),
    "stale_btn": (
        "⌛ Bu tugma eskirgan. Iltimos, menyudan qaytadan boshlang.",
        "⌛ Эта кнопка устарела. Пожалуйста, начните заново из меню.",
        "⌛ This button has expired. Please start again from the menu.",
    ),
    "session_expired": (
        "⌛ Sessiya eskirgan. Iltimos, qaytadan boshlang.",
        "⌛ Сессия устарела. Пожалуйста, начните заново.",
        "⌛ The session has expired. Please start again.",
    ),
    "unknown_text": (
        "🤔 Buni eslatma yoki xarajat sifatida tushunmadim.\n\n"
        "Menyudan tanlang yoki shunday yozing:\n"
        "<i>ertaga soat 9 da shifokorga borishni eslat</i>\n"
        "<i>Non 5000</i>\n\n"
        "Yordam: /yordam",
        "🤔 Я не понял это ни как напоминание, ни как расход.\n\n"
        "Выберите в меню или напишите так:\n"
        "<i>завтра в 9 утра напомни сходить к врачу</i>\n"
        "<i>Хлеб 5000</i>\n\n"
        "Справка: /yordam",
        "🤔 I couldn't understand that as a reminder or an expense.\n\n"
        "Pick from the menu or write like this:\n"
        "<i>remind me tomorrow at 9am to see the doctor</i>\n"
        "<i>Bread 5000</i>\n\n"
        "Help: /yordam",
    ),

    # ------------------------------------------------------------ salomlashuv va yordam
    "welcome": (
        "👋 Assalomu alaykum, <b>{name}</b>!\n\n"
        "⏰ <b>Eslatma Bot</b>ga xush kelibsiz — hech narsani unutmaslik uchun eng qulay yordamchi.\n\n"
        "Men sizga yordam beraman:\n"
        "🤝 muhim <b>uchrashuvlar</b>ni o'z vaqtida eslataman\n"
        "💊 <b>dori</b> ichish vaqtini kuzataman\n"
        "✅ <b>vazifa</b> va <b>shaxsiy rejalaringiz</b>ni unutdirmayman\n"
        "⏱ tezkor <b>taymer</b>ni ishga tushiraman\n"
        "💰 <b>xarajatlaringiz</b>ni hisoblab boraman ($ da ham)\n\n"
        "✨ Eng oson usul — shunchaki yozing:\n"
        "<i>«ertaga soat 9 da shifokorga borishni eslat»</i>\n"
        "yoki xarajat: <i>«Non 5000»</i>\n\n"
        "Boshlash uchun pastdagi menyudan foydalaning 👇",
        "👋 Здравствуйте, <b>{name}</b>!\n\n"
        "⏰ Добро пожаловать в <b>Бот-напоминалку</b> — самого удобного помощника, чтобы ничего не забывать.\n\n"
        "Я помогу вам:\n"
        "🤝 вовремя напомню о важных <b>встречах</b>\n"
        "💊 прослежу за временем приёма <b>лекарств</b>\n"
        "✅ не дам забыть <b>задачи</b> и <b>личные планы</b>\n"
        "⏱ запущу быстрый <b>таймер</b>\n"
        "💰 буду вести учёт ваших <b>расходов</b> (в том числе в $)\n\n"
        "✨ Проще всего — просто напишите:\n"
        "<i>«завтра в 9 утра напомни сходить к врачу»</i>\n"
        "или расход: <i>«Хлеб 5000»</i>\n\n"
        "Для начала воспользуйтесь меню внизу 👇",
        "👋 Hello, <b>{name}</b>!\n\n"
        "⏰ Welcome to <b>Reminder Bot</b> — the easiest way to never forget anything.\n\n"
        "I can:\n"
        "🤝 remind you of important <b>meetings</b> on time\n"
        "💊 keep track of your <b>medication</b> times\n"
        "✅ keep your <b>tasks</b> and <b>personal plans</b> in check\n"
        "⏱ start a quick <b>timer</b>\n"
        "💰 track your <b>expenses</b> (with a $ equivalent)\n\n"
        "✨ The easiest way — just write:\n"
        "<i>“remind me tomorrow at 9am to see the doctor”</i>\n"
        "or an expense: <i>“Bread 5000”</i>\n\n"
        "Use the menu below to get started 👇",
    ),
    "help": (
        "ℹ️ <b>Yordam</b>\n\n"
        "Men <b>Eslatma Bot</b>man — uchrashuv, dori, vazifa va rejalaringizni o'z vaqtida eslataman, "
        "xarajatlaringizni hisoblab boraman.\n\n"
        "<b>Menyu:</b>\n"
        "➕ <b>Yangi eslatma</b> — tur, matn va vaqtni tanlang\n"
        "⏱ <b>Taymer</b> — tezkor sanoq (5 daqiqa, 1 soat va h.k.)\n"
        "📋 <b>Eslatmalarim</b> — barcha faol eslatmalar\n"
        "📅 <b>Bugun</b> — bugungi rejalar\n"
        "💰 <b>Xarajatlar</b> — pulim, xaridlar (nomi + narxi), $ da hisob\n"
        "⚙️ <b>Sozlamalar</b> — vaqt mintaqasi, kunlik xulosa, til\n\n"
        "✨ <b>Tezkor usul:</b> shunchaki yozing —\n"
        "<i>ertaga soat 9 da shifokorga borishni eslat</i>\n"
        "yoki xarajat: <i>Non 5000</i>\n\n"
        "🕒 <b>Vaqtni shunday yozing:</b>\n"
        "• <code>bugun 18:30</code>\n"
        "• <code>ertaga soat 9 da</code>\n"
        "• <code>30 daqiqadan keyin</code>, <code>2 soatdan keyin</code>\n"
        "• <code>dushanba 10:00</code>\n"
        "• <code>25.12 14:00</code> yoki <code>25.12.2026 14:00</code>\n"
        "• <code>15 mart kechqurun 7 da</code>\n"
        "<i>Soatni ikki nuqta bilan yozing: 9:30</i>\n\n"
        "🔁 Eslatma <b>takrorlanishi</b> mumkin: har kuni, har hafta, har oy, ish kunlari yoki "
        "<b>har N soatda</b> (dori uchun qulay).\n\n"
        "Eslatma vaqti kelganda tugmalar chiqadi: ✅ <b>Bajarildi</b> yoki ⏰ <b>Kechiktirish</b>.\n\n"
        "🌐 Tilni tanlash shart emas: qaysi tilda yozsangiz (o'zbekcha, русский, English), bot o'sha tilda javob beradi.\n"
        "🕒 Soat noto'g'ri ko'rinsa: /vaqt\n\n"
        "<b>Buyruqlar:</b> /yangi /taymer /eslatmalar /bugun /xarajatlar /sozlamalar /vaqt /bekor\n"
        "👥 Guruhda: <code>/eslat ertaga 9:00 yig'ilish</code>",
        "ℹ️ <b>Справка</b>\n\n"
        "Я <b>Бот-напоминалка</b>: вовремя напоминаю о встречах, лекарствах, задачах и планах, "
        "а также веду учёт расходов.\n\n"
        "<b>Меню:</b>\n"
        "➕ <b>Новое напоминание</b> — выберите тип, текст и время\n"
        "⏱ <b>Таймер</b> — быстрый отсчёт (5 минут, 1 час и т.д.)\n"
        "📋 <b>Мои напоминания</b> — все активные напоминания\n"
        "📅 <b>Сегодня</b> — планы на сегодня\n"
        "💰 <b>Расходы</b> — мои деньги, покупки (название + цена), пересчёт в $\n"
        "⚙️ <b>Настройки</b> — часовой пояс, ежедневная сводка, язык\n\n"
        "✨ <b>Быстрый способ:</b> просто напишите —\n"
        "<i>завтра в 9 утра напомни сходить к врачу</i>\n"
        "или расход: <i>Хлеб 5000</i>\n\n"
        "🕒 <b>Как писать время:</b>\n"
        "• <code>сегодня в 18:30</code>\n"
        "• <code>завтра в 9 утра</code>\n"
        "• <code>через 30 минут</code>, <code>через 2 часа</code>\n"
        "• <code>в понедельник в 10:00</code>\n"
        "• <code>25.12 14:00</code> или <code>25.12.2026 14:00</code>\n"
        "• <code>15 марта в 7 вечера</code>\n"
        "<i>Часы пишите через двоеточие: 9:30</i>\n\n"
        "🔁 Напоминание можно <b>повторять</b>: каждый день, неделю, месяц, по будням или "
        "<b>каждые N часов</b> (удобно для лекарств).\n\n"
        "Когда придёт время, появятся кнопки: ✅ <b>Выполнено</b> или ⏰ <b>Отложить</b>.\n\n"
        "🌐 Выбирать язык не нужно: на каком языке вы пишете (o'zbekcha, русский, English), на таком я и отвечаю.\n"
        "🕒 Если время неверное: /vaqt\n\n"
        "<b>Команды:</b> /yangi /taymer /eslatmalar /bugun /xarajatlar /sozlamalar /vaqt /bekor\n"
        "👥 В группе: <code>/eslat завтра 9:00 совещание</code>",
        "ℹ️ <b>Help</b>\n\n"
        "I'm <b>Reminder Bot</b>: I remind you of meetings, medication, tasks and plans on time "
        "and keep track of your expenses.\n\n"
        "<b>Menu:</b>\n"
        "➕ <b>New reminder</b> — choose a type, text and time\n"
        "⏱ <b>Timer</b> — quick countdown (5 minutes, 1 hour, etc.)\n"
        "📋 <b>My reminders</b> — all active reminders\n"
        "📅 <b>Today</b> — today's plans\n"
        "💰 <b>Expenses</b> — my money, purchases (name + price), $ conversion\n"
        "⚙️ <b>Settings</b> — time zone, daily digest, language\n\n"
        "✨ <b>Quick way:</b> just write —\n"
        "<i>remind me tomorrow at 9am to see the doctor</i>\n"
        "or an expense: <i>Bread 5000</i>\n\n"
        "🕒 <b>How to write the time:</b>\n"
        "• <code>today 18:30</code>\n"
        "• <code>tomorrow at 9am</code>\n"
        "• <code>in 30 minutes</code>, <code>in 2 hours</code>\n"
        "• <code>monday 10:00</code>\n"
        "• <code>25.12 14:00</code> or <code>25.12.2026 14:00</code>\n"
        "• <code>March 15 at 7 pm</code>\n"
        "<i>Write hours with a colon: 9:30</i>\n\n"
        "🔁 A reminder can <b>repeat</b>: daily, weekly, monthly, on weekdays or "
        "<b>every N hours</b> (handy for medication).\n\n"
        "When it's time, buttons appear: ✅ <b>Done</b> or ⏰ <b>Snooze</b>.\n\n"
        "🌐 No need to pick a language: I answer in the language you write in (o'zbekcha, русский, English).\n"
        "🕒 If the time looks wrong: /vaqt\n\n"
        "<b>Commands:</b> /yangi /taymer /eslatmalar /bugun /xarajatlar /sozlamalar /vaqt /bekor\n"
        "👥 In a group: <code>/eslat tomorrow 9:00 meeting</code>",
    ),

    # ------------------------------------------------------------ bot profili (BotFather'dagi tavsif)
    "profile_short": (
        "Uchrashuv, dori, vazifa va rejalaringizni o'z vaqtida eslataman. Taymer va xarajatlar hisobi ham bor! ⏰",
        "Напомню о встречах, лекарствах, задачах и планах вовремя. Есть таймер и учёт расходов! ⏰",
        "I'll remind you of meetings, meds, tasks and plans on time. Timer and expense tracker included! ⏰",
    ),
    "profile_desc": (
        "⏰ Hech narsani unutmang!\n\n"
        "Men — shaxsiy eslatma yordamchingizman:\n"
        "🤝 muhim uchrashuvlar\n💊 dori ichish vaqti\n✅ kundalik vazifalar\n🎯 shaxsiy rejalar\n"
        "💰 xarajatlar hisobi ($ da ham)\n\n"
        "Bir martalik yoki takroriy eslatma qo'ying, taymerni ishga tushiring — qolganini menga qo'yib bering.\n\n"
        "Boshlash uchun «Start» tugmasini bosing 👇",
        "⏰ Ничего не забывайте!\n\n"
        "Я — ваш личный помощник-напоминалка:\n"
        "🤝 важные встречи\n💊 время приёма лекарств\n✅ ежедневные задачи\n🎯 личные планы\n"
        "💰 учёт расходов (в том числе в $)\n\n"
        "Ставьте разовые или повторяющиеся напоминания, запускайте таймер — остальное оставьте мне.\n\n"
        "Нажмите «Start», чтобы начать 👇",
        "⏰ Never forget anything!\n\n"
        "I'm your personal reminder assistant:\n"
        "🤝 important meetings\n💊 medication times\n✅ daily tasks\n🎯 personal plans\n"
        "💰 expense tracking (with a $ equivalent)\n\n"
        "Set one-time or repeating reminders, start a timer — leave the rest to me.\n\n"
        "Press “Start” to begin 👇",
    ),

    # ------------------------------------------------------------ buyruqlar menyusi
    "cmd_start": ("Botni boshlash", "Запустить бота", "Start the bot"),
    "cmd_new": ("Yangi eslatma qo'shish", "Новое напоминание", "New reminder"),
    "cmd_timer": ("Taymerni ishga tushirish", "Запустить таймер", "Start a timer"),
    "cmd_list": ("Faol eslatmalarim", "Мои активные напоминания", "My active reminders"),
    "cmd_today": ("Bugungi eslatmalar", "Напоминания на сегодня", "Today's reminders"),
    "cmd_expenses": ("Xarajatlar va pulim", "Расходы и мои деньги", "Expenses and my money"),
    "cmd_settings": ("Vaqt mintaqasi, til, sozlamalar", "Часовой пояс, язык, настройки", "Time zone, language, settings"),
    "cmd_time": ("Soat va vaqt mintaqasini tekshirish", "Проверить время и часовой пояс", "Check the time and time zone"),
    "cmd_help": ("Yordam va vaqt yozish misollari", "Справка и примеры времени", "Help and time examples"),
    "cmd_cancel": ("Joriy amalni bekor qilish", "Отменить текущее действие", "Cancel the current action"),
    "cmd_admin": ("Admin paneli", "Панель администратора", "Admin panel"),
    "cmd_group_remind": (
        "Guruhga eslatma: /eslat ertaga 9:00 yig'ilish",
        "Напоминание в группу: /eslat завтра 9:00 совещание",
        "Group reminder: /eslat tomorrow 9:00 meeting",
    ),
    "cmd_group_list": ("Guruhning faol eslatmalari", "Активные напоминания группы", "The group's active reminders"),

    # ------------------------------------------------------------ admin paneli
    "admin_panel": (
        "🛠 <b>Admin paneli</b>\n\nKerakli bo'limni tanlang:",
        "🛠 <b>Панель администратора</b>\n\nВыберите раздел:",
        "🛠 <b>Admin panel</b>\n\nChoose a section:",
    ),
    "admin_btn_stats": ("📊 Statistika", "📊 Статистика", "📊 Statistics"),
    "admin_btn_backup": ("💾 Backup", "💾 Резервная копия", "💾 Backup"),
    "admin_btn_broadcast": ("📣 Xabar yuborish", "📣 Рассылка", "📣 Broadcast"),
    "admin_btn_send": ("✅ Yuborish", "✅ Отправить", "✅ Send"),
    "admin_stats": (
        "📊 <b>Statistika</b>\n\n"
        "👥 Foydalanuvchilar: <b>{users_total}</b>\n"
        "   • so'nggi 7 kunda faol: {active7}\n"
        "   • botni bloklaganlar: {blocked}\n"
        "   • kunlik xulosa yoqilgan: {digest}\n\n"
        "⏰ <b>Eslatmalar</b>\n"
        "   • faol: {active}\n"
        "   • yuborilgan: {sent}\n"
        "   • bajarilgan: {done}\n"
        "   • yetkazib bo'lmagan: {failed}\n"
        "   • oxirgi 24 soatda yaratilgan: {created}\n"
        "   • keyingi 24 soatda yuboriladi: {next}\n\n"
        "💰 <b>Xarajatlar</b>\n"
        "   • hamyonlar: {wallets}\n"
        "   • xaridlar: {expenses}",
        "📊 <b>Статистика</b>\n\n"
        "👥 Пользователи: <b>{users_total}</b>\n"
        "   • активны за 7 дней: {active7}\n"
        "   • заблокировали бота: {blocked}\n"
        "   • включена ежедневная сводка: {digest}\n\n"
        "⏰ <b>Напоминания</b>\n"
        "   • активные: {active}\n"
        "   • отправленные: {sent}\n"
        "   • выполненные: {done}\n"
        "   • не доставлено: {failed}\n"
        "   • создано за 24 часа: {created}\n"
        "   • будет отправлено в ближайшие 24 часа: {next}\n\n"
        "💰 <b>Расходы</b>\n"
        "   • кошельки: {wallets}\n"
        "   • покупки: {expenses}",
        "📊 <b>Statistics</b>\n\n"
        "👥 Users: <b>{users_total}</b>\n"
        "   • active in the last 7 days: {active7}\n"
        "   • blocked the bot: {blocked}\n"
        "   • daily digest enabled: {digest}\n\n"
        "⏰ <b>Reminders</b>\n"
        "   • active: {active}\n"
        "   • sent: {sent}\n"
        "   • done: {done}\n"
        "   • undeliverable: {failed}\n"
        "   • created in the last 24 hours: {created}\n"
        "   • due in the next 24 hours: {next}\n\n"
        "💰 <b>Expenses</b>\n"
        "   • wallets: {wallets}\n"
        "   • purchases: {expenses}",
    ),
    "admin_backup_wait": ("⏳ Zaxira tayyorlanmoqda…", "⏳ Готовлю резервную копию…", "⏳ Preparing the backup…"),
    "admin_backup_caption": ("💾 Zaxira: <code>{name}</code>", "💾 Копия: <code>{name}</code>", "💾 Backup: <code>{name}</code>"),
    "admin_bc_prompt": (
        "📣 <b>Xabar yuborish</b>\n\nBarcha foydalanuvchilarga yuboriladigan xabarni yuboring "
        "(matn, rasm, video — formati saqlanadi).\n\nBekor qilish: /bekor",
        "📣 <b>Рассылка</b>\n\nОтправьте сообщение для всех пользователей "
        "(текст, фото, видео — формат сохранится).\n\nОтмена: /bekor",
        "📣 <b>Broadcast</b>\n\nSend the message for all users "
        "(text, photo, video — the format is preserved).\n\nCancel: /bekor",
    ),
    "admin_bc_confirm": (
        "👆 Shu xabar <b>{n}</b> ta foydalanuvchiga yuboriladi. Tasdiqlaysizmi?",
        "👆 Это сообщение получат <b>{n}</b> пользователей. Подтверждаете?",
        "👆 This message will be sent to <b>{n}</b> users. Confirm?",
    ),
    "admin_bc_cancelled": ("❌ Yuborish bekor qilindi.", "❌ Рассылка отменена.", "❌ Broadcast cancelled."),
    "admin_bc_started": (
        "🚀 Yuborish boshlandi: <b>{n}</b> ta foydalanuvchi…",
        "🚀 Рассылка началась: <b>{n}</b> пользователей…",
        "🚀 Broadcast started: <b>{n}</b> users…",
    ),
    "admin_bc_report": (
        "✅ <b>Yuborish tugadi</b>\n\n📬 Yetkazildi: <b>{sent}</b>\n⚠️ Xato / bloklagan: <b>{failed}</b>",
        "✅ <b>Рассылка завершена</b>\n\n📬 Доставлено: <b>{sent}</b>\n⚠️ Ошибки / заблокировали: <b>{failed}</b>",
        "✅ <b>Broadcast finished</b>\n\n📬 Delivered: <b>{sent}</b>\n⚠️ Failed / blocked: <b>{failed}</b>",
    ),
}
