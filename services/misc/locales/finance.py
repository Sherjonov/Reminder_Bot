"""Xarajatlar (hamyon, xaridlar, tarix). Tartib: (uz, ru, en)."""

MESSAGES: dict[str, tuple[str, str, str]] = {
    # ------------------------------------------------------------ bosh ekran
    "fin_title": ("💰 <b>Xarajatlar</b>", "💰 <b>Расходы</b>", "💰 <b>Expenses</b>"),
    "fin_l_balance": ("💼 <b>Umumiy summa:</b> {v}", "💼 <b>Общая сумма:</b> {v}", "💼 <b>Total amount:</b> {v}"),
    "fin_l_usd": ("      💵 ≈ {v}", "      💵 ≈ {v}", "      💵 ≈ {v}"),
    "fin_unset": ("kiritilmagan", "не указана", "not set"),
    "fin_l_spent": ("📉 <b>Jami sarflandi:</b> {v}", "📉 <b>Всего потрачено:</b> {v}", "📉 <b>Total spent:</b> {v}"),
    "fin_l_count": ("🧾 Xaridlar soni: <b>{n}</b>", "🧾 Покупок: <b>{n}</b>", "🧾 Purchases: <b>{n}</b>"),
    "fin_l_today": ("📅 Bugun: <b>{v}</b>", "📅 Сегодня: <b>{v}</b>", "📅 Today: <b>{v}</b>"),
    "fin_l_month": ("🗓 Shu oy: <b>{v}</b>", "🗓 В этом месяце: <b>{v}</b>", "🗓 This month: <b>{v}</b>"),
    "fin_l_rate": (
        "💱 Kurs: 1 $ = {rate} so'm ({date})",
        "💱 Курс: 1 $ = {rate} сум ({date})",
        "💱 Rate: 1 $ = {rate} UZS ({date})",
    ),
    "fin_no_rate": (
        "💱 Dollar kursi hozircha mavjud emas.",
        "💱 Курс доллара пока недоступен.",
        "💱 The dollar rate is unavailable right now.",
    ),
    "fin_hint_unset": (
        "ℹ️ Pulingiz qancha ekanini kiriting: «✏️ Umumiy summani o'zgartirish». Keyin har bir xarid shu summadan ayriladi.",
        "ℹ️ Укажите, сколько у вас денег: «✏️ Изменить общую сумму». Дальше каждая покупка будет вычитаться из неё.",
        "ℹ️ Enter how much money you have: “✏️ Change total amount”. Then every purchase will be deducted from it.",
    ),
    "fin_neg_warn": (
        "⚠️ Hisobingizdagi mablag' yetmadi: qoldiq manfiy.",
        "⚠️ Денег не хватило: остаток отрицательный.",
        "⚠️ Not enough funds: the balance is negative.",
    ),

    # ------------------------------------------------------------ tugmalar
    "fb_add": ("➕ Xarajat qo'shish", "➕ Добавить расход", "➕ Add expense"),
    "fb_list": ("📋 Xaridlar ro'yxati", "📋 Список покупок", "📋 Purchases"),
    "fb_set": ("✏️ Umumiy summani o'zgartirish", "✏️ Изменить общую сумму", "✏️ Change total amount"),
    "fb_topup": ("💵 Pul qo'shish", "💵 Пополнить", "💵 Add money"),
    "fb_log": ("🕘 Balans tarixi", "🕘 История баланса", "🕘 Balance history"),
    "fb_done": ("✅ Tayyor", "✅ Готово", "✅ Done"),
    "fb_undo": ("↩️ Bekor qilish", "↩️ Отменить", "↩️ Undo"),
    "fb_home": ("⬅️ Xarajatlar", "⬅️ Расходы", "⬅️ Expenses"),
    "fb_edit_title": ("✏️ Nomi", "✏️ Название", "✏️ Name"),
    "fb_edit_price": ("💲 Narxi", "💲 Цена", "💲 Price"),
    "fb_delete": ("🗑 O'chirish", "🗑 Удалить", "🗑 Delete"),
    "fb_yes_add": ("✅ Qo'shish", "✅ Добавить", "✅ Add"),
    "fb_no": ("❌ Yo'q", "❌ Нет", "❌ No"),

    # ------------------------------------------------------------ xarajat qo'shish
    "fin_add_prompt": (
        "➕ <b>Xarajat qo'shish</b>\n\nMahsulot nomi va narxini yozing:\n"
        "• <code>Non 5000</code>\n• <code>Go'sht 85 ming</code>\n• <code>Telefon 1.2 mln</code>\n"
        "• <code>Kitob $12</code> (dollarda ham bo'ladi)\n\n"
        "Bir nechta mahsulotni har birini yangi qatordan yozishingiz mumkin. Har bir xarid umumiy summadan ayriladi.\n\n"
        "Tugatgach «✅ Tayyor» ni bosing.",
        "➕ <b>Добавить расход</b>\n\nНапишите название и цену:\n"
        "• <code>Хлеб 5000</code>\n• <code>Мясо 85 тыс</code>\n• <code>Телефон 1.2 млн</code>\n"
        "• <code>Книга $12</code> (можно и в долларах)\n\n"
        "Можно несколько товаров — каждый с новой строки. Каждая покупка вычитается из общей суммы.\n\n"
        "Когда закончите, нажмите «✅ Готово».",
        "➕ <b>Add an expense</b>\n\nWrite the product name and price:\n"
        "• <code>Bread 5000</code>\n• <code>Meat 85k</code>\n• <code>Phone 1.2 mln</code>\n"
        "• <code>Book $12</code> (dollars work too)\n\n"
        "You can add several items — one per line. Each purchase is deducted from your total amount.\n\n"
        "Press “✅ Done” when you're finished.",
    ),
    "fin_added_title": ("✅ <b>Qo'shildi</b>", "✅ <b>Добавлено</b>", "✅ <b>Added</b>"),
    "fin_item": ("• {name} — {amount}", "• {name} — {amount}", "• {name} — {amount}"),
    "fin_added_total": ("Jami: <b>{v}</b>", "Итого: <b>{v}</b>", "Total: <b>{v}</b>"),
    "fin_remaining": ("💼 Qoldiq: <b>{v}</b>", "💼 Остаток: <b>{v}</b>", "💼 Remaining: <b>{v}</b>"),
    "fin_not_deducted": (
        "ℹ️ Umumiy summa kiritilmagani uchun hech narsa ayrilmadi («✏️ Umumiy summani o'zgartirish» orqali kiriting).",
        "ℹ️ Общая сумма не указана, поэтому ничего не вычтено (укажите её через «✏️ Изменить общую сумму»).",
        "ℹ️ Your total amount isn't set, so nothing was deducted (set it via “✏️ Change total amount”).",
    ),
    "fin_line_bad": (
        "🤔 Tushunmadim: «{line}». Shunday yozing: <code>Non 5000</code>",
        "🤔 Не понял: «{line}». Пишите так: <code>Хлеб 5000</code>",
        "🤔 I didn't get: “{line}”. Write like this: <code>Bread 5000</code>",
    ),
    "fin_ask_price": (
        "💬 «{name}» narxini yozing (masalan: <code>5000</code> yoki <code>5 ming</code>)",
        "💬 Напишите цену для «{name}» (например: <code>5000</code> или <code>5 тыс</code>)",
        "💬 Write the price for “{name}” (e.g. <code>5000</code> or <code>5k</code>)",
    ),
    "fin_ask_name": (
        "✍️ Mahsulot nomini ham yozing: <code>Non 5000</code>",
        "✍️ Напишите ещё и название товара: <code>Хлеб 5000</code>",
        "✍️ Please include the product name too: <code>Bread 5000</code>",
    ),
    "fin_amount_bad": (
        "🤔 Summani tushunmadim. Masalan: <code>5000</code>, <code>85 ming</code>, <code>1.2 mln</code>",
        "🤔 Не понял сумму. Например: <code>5000</code>, <code>85 тыс</code>, <code>1.2 млн</code>",
        "🤔 I couldn't understand the amount. For example: <code>5000</code>, <code>85k</code>, <code>1.2 mln</code>",
    ),
    "fin_usd_no_rate": (
        "💱 Dollar kursi hozir mavjud emas — summani so'mda yozing.",
        "💱 Курс доллара сейчас недоступен — укажите сумму в сумах.",
        "💱 The dollar rate is unavailable right now — please enter the amount in UZS.",
    ),
    "fin_too_many": (
        "Bir xabarda {max} tadan ko'p mahsulot yozmang.",
        "Не добавляйте больше {max} товаров в одном сообщении.",
        "Please don't add more than {max} items in one message.",
    ),
    "fin_name_long": (
        "✂️ Mahsulot nomi juda uzun (eng ko'pi {max} belgi).",
        "✂️ Название слишком длинное (не более {max} символов).",
        "✂️ The product name is too long (up to {max} characters).",
    ),

    # ------------------------------------------------------------ umumiy summa
    "fin_set_prompt": (
        "✏️ <b>Umumiy summani o'zgartirish</b>\n\nHozir qancha pulingiz bor? Yangi umumiy summani yozing:\n"
        "• <code>2 mln</code>\n• <code>1 500 000</code>\n• <code>850 ming</code>\n\nHozirgi: <b>{current}</b>",
        "✏️ <b>Изменить общую сумму</b>\n\nСколько у вас сейчас денег? Напишите новую общую сумму:\n"
        "• <code>2 млн</code>\n• <code>1 500 000</code>\n• <code>850 тыс</code>\n\nСейчас: <b>{current}</b>",
        "✏️ <b>Change the total amount</b>\n\nHow much money do you have now? Write the new total:\n"
        "• <code>2 mln</code>\n• <code>1 500 000</code>\n• <code>850k</code>\n\nCurrent: <b>{current}</b>",
    ),
    "fin_set_done": (
        "✅ <b>Umumiy summa yangilandi</b>\n\n💼 {v}{usd}",
        "✅ <b>Общая сумма обновлена</b>\n\n💼 {v}{usd}",
        "✅ <b>Total amount updated</b>\n\n💼 {v}{usd}",
    ),
    "fin_topup_prompt": (
        "💵 <b>Pul qo'shish</b>\n\nQancha pul qo'shamiz? (masalan: <code>500 ming</code>)",
        "💵 <b>Пополнение</b>\n\nСколько денег добавить? (например: <code>500 тыс</code>)",
        "💵 <b>Add money</b>\n\nHow much shall we add? (e.g. <code>500k</code>)",
    ),
    "fin_topup_done": (
        "✅ <b>+{amount}</b> qo'shildi\n\n💼 Umumiy summa: <b>{v}</b>{usd}",
        "✅ <b>+{amount}</b> добавлено\n\n💼 Общая сумма: <b>{v}</b>{usd}",
        "✅ <b>+{amount}</b> added\n\n💼 Total amount: <b>{v}</b>{usd}",
    ),

    # ------------------------------------------------------------ ro'yxat va tafsilot
    "fin_list_title": (
        "🧾 <b>Xaridlar ro'yxati</b> — {total} ta",
        "🧾 <b>Список покупок</b> — {total}",
        "🧾 <b>Purchases</b> — {total}",
    ),
    "fin_list_empty": (
        "Hozircha xaridlar yo'q. «➕ Xarajat qo'shish» ni bosing.",
        "Покупок пока нет. Нажмите «➕ Добавить расход».",
        "No purchases yet. Press “➕ Add expense”.",
    ),
    "fin_list_item": (
        "<b>{i}.</b> {title} — <b>{amount}</b>\n      🕒 {when}",
        "<b>{i}.</b> {title} — <b>{amount}</b>\n      🕒 {when}",
        "<b>{i}.</b> {title} — <b>{amount}</b>\n      🕒 {when}",
    ),
    "fin_list_hint": (
        "<i>Batafsil ko'rish uchun raqamni bosing.</i>",
        "<i>Нажмите на номер, чтобы открыть подробности.</i>",
        "<i>Press a number to see the details.</i>",
    ),
    "fin_detail": (
        "🧾 <b>{title}</b>\n\n💸 Narxi: <b>{amount}</b>{usd}\n🕒 {when}{note}",
        "🧾 <b>{title}</b>\n\n💸 Цена: <b>{amount}</b>{usd}\n🕒 {when}{note}",
        "🧾 <b>{title}</b>\n\n💸 Price: <b>{amount}</b>{usd}\n🕒 {when}{note}",
    ),
    "fin_nodeduct_note": (
        "\nℹ️ Bu xarid umumiy summadan ayrilmagan.",
        "\nℹ️ Эта покупка не вычиталась из общей суммы.",
        "\nℹ️ This purchase was not deducted from the total amount.",
    ),
    "fin_edit_title_prompt": (
        "✏️ <b>Yangi nomni yozing</b>\n\nHozirgi: <i>{v}</i>",
        "✏️ <b>Напишите новое название</b>\n\nСейчас: <i>{v}</i>",
        "✏️ <b>Write the new name</b>\n\nCurrent: <i>{v}</i>",
    ),
    "fin_edit_price_prompt": (
        "💲 <b>Yangi narxni yozing</b>\n\nHozirgi: <b>{v}</b>",
        "💲 <b>Напишите новую цену</b>\n\nСейчас: <b>{v}</b>",
        "💲 <b>Write the new price</b>\n\nCurrent: <b>{v}</b>",
    ),
    "fin_updated": ("✅ <b>Yangilandi</b>\n\n{detail}", "✅ <b>Обновлено</b>\n\n{detail}", "✅ <b>Updated</b>\n\n{detail}"),
    "fin_del_confirm": (
        "🗑 <b>O'chirishni tasdiqlaysizmi?</b>\n\n{detail}",
        "🗑 <b>Подтвердить удаление?</b>\n\n{detail}",
        "🗑 <b>Confirm deletion?</b>\n\n{detail}",
    ),
    "fin_deleted": (
        "🗑 <b>O'chirildi</b>{refund}",
        "🗑 <b>Удалено</b>{refund}",
        "🗑 <b>Deleted</b>{refund}",
    ),
    "fin_refund_note": (
        "\n💼 Pul umumiy summaga qaytarildi: <b>{v}</b>",
        "\n💼 Деньги возвращены в общую сумму: <b>{v}</b>",
        "\n💼 The money was returned to your total: <b>{v}</b>",
    ),
    "fin_deleted_toast": ("🗑 O'chirildi", "🗑 Удалено", "🗑 Deleted"),
    "fin_not_found": ("Xarid topilmadi.", "Покупка не найдена.", "Purchase not found."),

    # ------------------------------------------------------------ tarix
    "fin_log_title": ("🕘 <b>Balans tarixi</b>", "🕘 <b>История баланса</b>", "🕘 <b>Balance history</b>"),
    "fin_log_empty": ("Hozircha harakatlar yo'q.", "Пока нет движений.", "No activity yet."),
    "fin_log_line": (
        "• {when} · {label}: <b>{delta}</b> → {balance}",
        "• {when} · {label}: <b>{delta}</b> → {balance}",
        "• {when} · {label}: <b>{delta}</b> → {balance}",
    ),
    "fin_k_set": ("Summa o'rnatildi", "Сумма установлена", "Total set"),
    "fin_k_topup": ("Pul qo'shildi", "Пополнение", "Money added"),
    "fin_k_expense": ("Xarid", "Покупка", "Purchase"),
    "fin_k_refund": ("Qaytarildi", "Возврат", "Refund"),
    "fin_k_edit": ("Tuzatish", "Корректировка", "Adjustment"),

    # ------------------------------------------------------------ tezkor qo'shish va bekor qilish
    "fin_quick_ask": (
        "💰 Xarajat sifatida qo'shaymi?\n\n{items}\n\nJami: <b>{total}</b>",
        "💰 Добавить как расход?\n\n{items}\n\nИтого: <b>{total}</b>",
        "💰 Add as an expense?\n\n{items}\n\nTotal: <b>{total}</b>",
    ),
    "fin_quick_cancelled": ("Bekor qilindi.", "Отменено.", "Cancelled."),
    "fin_undone": (
        "↩️ Bekor qilindi — {n} ta xarid o'chirildi, pul qaytarildi.",
        "↩️ Отменено — удалено покупок: {n}, деньги возвращены.",
        "↩️ Undone — {n} purchase(s) removed, money returned.",
    ),
    "fin_undo_none": ("Bekor qilinadigan xarid yo'q.", "Нечего отменять.", "Nothing to undo."),
}
