# ⏰ Eslatma Bot (Reminder Bot)

Telegram bot: **uchrashuv, dori ichish vaqti, vazifa va shaxsiy rejalaringizni** o'z vaqtida eslatadi,
tezkor **taymer** ishga tushiradi va **xarajatlaringizni** (so'mda va $ da) hisoblab boradi.
Ma'lumotlar **MySQL** (`reminder_bot` bazasi) da saqlanadi — bot o'chib-yonsa ham hech narsa yo'qolmaydi.

🌐 **3 tilda** — o'zbekcha, русский, English. Bot tili **siz yozgan tilga qarab o'zi almashadi**.

## ✨ Imkoniyatlar

| Bo'lim | Nima qiladi |
|---|---|
| ➕ **Yangi eslatma** | Tur (🤝 uchrashuv, 💊 dori, ✅ vazifa, 🎯 reja, 🔔 boshqa) → matn → vaqt → takrorlanish → tasdiqlash |
| ✍️ **Tezkor yozuv** | Shunchaki yozing: *«ertaga soat 9 da shifokorga borishni eslat»* — bot vaqt va matnni o'zi ajratadi |
| 🔁 **Takrorlanish** | Bir marta · har kuni · har hafta · har oy · ish kunlari · har yili · **har N soatda** (dori uchun) |
| ⏱ **Taymer** | 5 / 10 / 15 / 30 / 45 daqiqa, 1–2 soat yoki o'zingiz yozgan vaqt (`1:30`, `45 daqiqa`) |
| ⏰ **Eslatma vaqtida** | ✅ Bajarildi · ⏰ 10 daqiqa / 30 daqiqa / 1 soatga kechiktirish |
| 📋 **Eslatmalarim / 📅 Bugun** | Sahifalangan ro'yxat, matn/vaqtni tahrirlash, o'chirish |
| 🌅 **Kunlik xulosa** | Ertalab bugungi eslatmalar ro'yxati (Sozlamalarda yoqiladi) |
| 🌍 **Vaqt mintaqasi** | Standart — Toshkent (UTC+5); Moskva, Seul, Istanbul… yoki `+9`, `Asia/Tokyo` |
| 👥 **Guruhlarda** | `/eslat ertaga 9:00 yig'ilish`, `/eslatmalar` |
| 💰 **Xarajatlar** | **Umumiy summa** (sizda bor pul, o'zgartirib turiladi) · xarid = **mahsulot nomi + narxi** (`Non 5000`, `Go'sht 85 ming`, `Telefon 1.2 mln`, `Kitob $12`) · har bir xarid umumiy summadan **avtomatik ayriladi** · summa so'mda, **tagida $ da** (CBU kursi) · ro'yxat, tahrirlash, o'chirish (pul qaytadi), bekor qilish, balans tarixi |
| 🕒 **To'g'ri vaqt** | Bot soatni Telegram serveri vaqtiga moslaydi (kompyuter soati yoki Windows vaqt mintaqasi xato bo'lsa ham); `/vaqt` — tekshirish; **Sozlamalar → «Soatim noto'g'ri»** — telefoningizdagi soatni yozsangiz, bot o'zi moslab oladi |
| 🛠 **Admin paneli** | `/admin` — statistika, bazani zaxiralash (backup), barcha foydalanuvchilarga xabar yuborish |

### 🕒 Vaqtni qanday yozish mumkin

```
bugun 18:30          ertaga soat 9 da        30 daqiqadan keyin     2 soatdan keyin
dushanba 10:00       25.12 14:00             25.12.2026 09:00       15 mart kechqurun 7 da
ertaga tushdan keyin soat 3 da               1 soat 30 daqiqadan keyin
```

> Soatni **ikki nuqta** bilan yozing (`9:30`). Nuqtali `10.12` — sana (10-dekabr) deb tushuniladi.

## 🚀 Ishga tushirish (Windows / VS Code, Python 3.14)

1. **Baza.** HeidiSQL'da `reminder_bot` bazasi allaqachon bor. Jadvallarni bot **o'zi yaratadi** (birinchi ishga tushishda).
   Xohlasangiz qo'lda: HeidiSQL → `reminder_bot` ni tanlang → `services/db_api/schema.sql` ni oching va ishga tushiring (F9).
2. **Kutubxonalar:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **`.env` ni to'ldiring** (namuna — `.env.example`):
   - `BOT_TOKEN` — @BotFather dan olingan token
   - `ADMINS` — sizning Telegram ID ingiz (@userinfobot dan bilib oling)
   - `DB_USER` / `DB_PASSWORD` — HeidiSQL'ga kirishda ishlatadigan login va parol
4. **Ishga tushiring:**
   ```bash
   python main.py
   ```
5. Telegramda botni oching va `/start` ni bosing.

### BotFather'da (bir marta)
- `/setdescriptionpic` → `assets/description_pic.jpg` ni yuklang (bot profilidagi rasm).
- Bot nomi va tavsif matnlari: tavsif (Description / About) ishga tushganda avtomatik o'rnatiladi
  (`SET_BOT_PROFILE=false` qilsangiz tegilmaydi). Buyruqlar menyusi ham avtomatik.

## 🗂 Loyiha tuzilmasi (Telegram-bot shabloni bo'yicha)

```
reminder_bot/
├── assets/                  welcome.jpg (/start rasmi), description_pic.jpg (BotFather uchun)
├── config/config.py         .env dan sozlamalar
├── data/                    backups/ — bazaning SQL zaxiralari
├── filters/                 is_admin.py, text_filters.py (menyu tugmalari), chat_type.py
├── handlers/
│   ├── errors.py            xatolarni ushlash + adminga xabar
│   ├── admins/              panel.py (statistika, backup), broadcast.py (ommaviy xabar)
│   ├── groups/              group_reminders.py (/eslat, /eslatmalar)
│   └── users/               menu, start, new_reminder, quick_add, my_reminders, timer,
│                            expenses (xarajatlar), preferences (sozlamalar), fired, fallback
├── keyboards/
│   ├── styles.py            tugma matnlari va ranglari (primary / success / danger)
│   ├── default/             pastdagi asosiy menyu
│   └── inline/              callbacks.py, reminders.py, settings.py, admin.py
├── middlewares/             throttling.py, user_context.py, language.py (tilni avtomatik aniqlash)
├── services/
│   ├── db_api/              database.py (pul + tranzaksiya + migratsiya), users.py, reminders.py,
│   │                        finance.py (hamyon/xaridlar SQL), schema.sql
│   ├── misc/                time_parser.py (uz/ru/en vaqt iboralari), money.py (summa tahlili), i18n.py,
│   │                        langdetect.py, locales/ (uz·ru·en matnlar), recurrence.py, formatting.py,
│   │                        timeutils.py, constants.py
│   ├── finance.py           xarajatlar biznes-mantig'i (atomar tranzaksiyalar, jurnal)
│   ├── currency.py          USD kursi: CBU -> zaxira manba -> baza keshi
│   ├── time_sync.py         soatni Telegram serveri vaqtiga moslash
│   ├── scheduler.py         eslatmalarni vaqtida yuboruvchi sikl + kunlik xulosa
│   ├── backup.py · bot_profile.py · flow.py · health_server.py · messaging.py
│   └── notify_admins.py · set_bot_commands.py · welcome.py
├── states/states.py         FSM holatlari
├── .env  .env.example  .gitignore
├── main.py
├── README.md
└── requirements.txt
```

## ⚙️ Qanday ishlaydi

- Barcha vaqtlar bazada **UTC** da saqlanadi, foydalanuvchiga uning vaqt mintaqasida ko'rsatiladi.
- `services/scheduler.py` har `SCHEDULER_TICK` (10) soniyada `reminders` jadvalidan vaqti kelganlarini oladi va yuboradi.
  Bot o'chiq paytda kelgan eslatmalar yoqilganda **«kechikib yetkazildi»** belgisi bilan yuboriladi.
- Takrorlanuvchi eslatmalarda keyingi vaqt mahalliy soat bo'yicha hisoblanadi (yozgi/qishki vaqtga o'tishda ham bir xil soatda keladi).
- Botni bloklagan foydalanuvchining eslatmalari to'xtatiladi; yana yozsa, qayta faollashadi.
- FSM holati xotirada (`MemoryStorage`) — bot qayta ishga tushsa, yarim qolgan suhbat bekor bo'ladi, **saqlangan eslatmalar** esa yo'qolmaydi.

## ☁️ Hostingga (Render va h.k.) joylash

- `HEALTH_SERVER=true` bo'lsa, bot `PORT` portida `GET /health` ni ochadi — Render "Web Service" uchun "No open ports detected" xatosi chiqmaydi.
- Hostingda MySQL ham kerak: tashqi MySQL xizmatini ulang va `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` ni yangilang.
- `data/backups/` hostingda vaqtinchalik bo'lishi mumkin — zaxiralar adminlarga Telegram orqali ham yuboriladi.

## 🧩 Shu tuzilmada keyingi botlar

Papkalar bir xil qoladi; faqat `services/db_api/` (jadvallar), `handlers/users/` va `keyboards/` almashadi.

## 💰 Xarajatlar qanday ishlaydi

1. **💰 Xarajatlar → ✏️ Umumiy summani o'zgartirish** — hozir qancha pulingiz borligini yozing (`2 mln`, `850 ming`, `1 500 000`).
2. **➕ Xarajat qo'shish** — `Non 5000`, `Sut 12 000`, `Go'sht 85 ming` (har birini yangi qatordan, bir xabarda ko'p mahsulot ham mumkin).
   Yoki rejimga kirmay, shunchaki `Non 5000` deb yozing — bot «xarajat sifatida qo'shaymi?» deb so'raydi.
3. Har bir xarid **umumiy summadan ayriladi**. Ekranda: tepada **so'mda**, uning tagida **$ da** hisob. Pul yetmasa, qoldiq manfiy bo'ladi va ogohlantiriladi.
4. Xaridni o'chirsangiz pul qaytadi, narxini o'zgartirsangiz farq hisobga olinadi. **🕘 Balans tarixi** barcha harakatlarni ko'rsatadi.

Backend: barcha pul o'zgarishlari **bitta tranzaksiyada** (`SELECT ... FOR UPDATE` bilan), har biri `wallet_log` jurnaliga yoziladi,
jadvallar `ON DELETE CASCADE`, eski bazalar avtomatik **migratsiya** qilinadi. Dollar kursi O'zbekiston Markaziy bankidan
(`cbu.uz`) olinadi, 3 soatda bir yangilanadi va bazada keshlanadi.

## 🌐 Til

Siz qaysi tilda yozsangiz, bot shu tilda javob beradi (menyu tugmalari ham almashadi). Tilni qo'lda tanlash: **Sozlamalar → 🌐 Til**.
Vaqt iboralari uchala tilda tushuniladi: `ertaga soat 9 da` · `завтра в 9 утра` · `tomorrow at 9am`.
