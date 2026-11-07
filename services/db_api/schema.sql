-- Eslatma Bot — ma'lumotlar bazasi sxemasi (MySQL 5.7+ / MariaDB 10.3+).
-- Bot ishga tushganda bu fayl avtomatik bajariladi (CREATE TABLE IF NOT EXISTS),
-- xohlasangiz HeidiSQL'da `reminder_bot` bazasini tanlab, qo'lda ham ishga tushirishingiz mumkin.
-- Barcha vaqtlar UTC da saqlanadi.

CREATE TABLE IF NOT EXISTS `users` (
  `user_id`          BIGINT       NOT NULL,                       -- Telegram ID
  `username`         VARCHAR(64)  NULL,
  `full_name`        VARCHAR(255) NOT NULL DEFAULT '',
  `language_code`    VARCHAR(16)  NULL,                       -- Telegram ilovasidagi til
  `language`         VARCHAR(2)   NOT NULL DEFAULT 'uz',     -- bot tili: uz | ru | en (foydalanuvchi yozishiga qarab o'zgaradi)
  `timezone`         VARCHAR(64)  NOT NULL DEFAULT 'Asia/Tashkent',
  `digest_enabled`   TINYINT(1)   NOT NULL DEFAULT 0,             -- ertalabki kunlik xulosa
  `last_digest_date` DATE         NULL,
  `is_blocked`       TINYINT(1)   NOT NULL DEFAULT 0,             -- foydalanuvchi botni bloklagan
  `created_at`       DATETIME     NOT NULL,
  `last_active`      DATETIME     NOT NULL,
  PRIMARY KEY (`user_id`),
  KEY `idx_users_digest` (`digest_enabled`, `is_blocked`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `reminders` (
  `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id`       BIGINT          NOT NULL,                       -- eslatma egasi
  `chat_id`       BIGINT          NOT NULL,                       -- qayerga yuboriladi (shaxsiy chat yoki guruh)
  `category`      VARCHAR(16)     NOT NULL DEFAULT 'other',       -- meeting | medicine | task | plan | other | timer
  `text`          VARCHAR(1000)   NOT NULL,
  `remind_at`     DATETIME        NOT NULL,                       -- keyingi eslatish vaqti (UTC)
  `timezone`      VARCHAR(64)     NOT NULL DEFAULT 'Asia/Tashkent',
  `repeat_type`   VARCHAR(16)     NOT NULL DEFAULT 'none',        -- none | daily | weekly | monthly | yearly | weekdays | interval
  `repeat_value`  INT             NULL,                           -- interval: daqiqa; monthly: oy kuni
  `duration_min`  INT             NULL,                           -- taymer davomiyligi (daqiqa)
  `status`        VARCHAR(12)     NOT NULL DEFAULT 'active',      -- active | sent | done | failed
  `parent_id`     BIGINT UNSIGNED NULL,                           -- kechiktirilgan nusxa uchun asl eslatma
  `fired_count`   INT             NOT NULL DEFAULT 0,
  `created_at`    DATETIME        NOT NULL,
  `last_sent_at`  DATETIME        NULL,
  PRIMARY KEY (`id`),
  KEY `idx_rem_due` (`status`, `remind_at`),
  KEY `idx_rem_user` (`user_id`, `status`, `remind_at`),
  KEY `idx_rem_chat` (`chat_id`, `status`),
  CONSTRAINT `fk_rem_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------- xarajatlar moduli
-- Hamyon: foydalanuvchining "umumiy summasi" (so'mda). Har bir xarid shu summadan ayriladi.
CREATE TABLE IF NOT EXISTS `wallets` (
  `user_id`    BIGINT   NOT NULL,
  `balance`    BIGINT   NOT NULL DEFAULT 0,          -- joriy qoldiq (so'm); manfiy bo'lishi mumkin
  `is_set`     TINYINT(1) NOT NULL DEFAULT 0,        -- foydalanuvchi summani kiritganmi
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `fk_wallet_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Xaridlar: mahsulot nomi va narxi (so'mda).
CREATE TABLE IF NOT EXISTS `expenses` (
  `id`         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id`    BIGINT          NOT NULL,
  `title`      VARCHAR(200)    NOT NULL,
  `amount`     BIGINT UNSIGNED NOT NULL,             -- so'm
  `deducted`   TINYINT(1)      NOT NULL DEFAULT 1,   -- xarid paytida umumiy summadan ayrilganmi
  `created_at` DATETIME        NOT NULL,             -- UTC
  PRIMARY KEY (`id`),
  KEY `idx_exp_user_date` (`user_id`, `created_at`),
  CONSTRAINT `fk_exp_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Hamyon harakatlari jurnali (audit): har bir o'zgarish shu yerga yoziladi.
CREATE TABLE IF NOT EXISTS `wallet_log` (
  `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id`       BIGINT          NOT NULL,
  `kind`          VARCHAR(12)     NOT NULL,          -- set | topup | expense | refund | edit
  `delta`         BIGINT          NOT NULL,          -- o'zgarish (+ qo'shildi, - ayrildi)
  `balance_after` BIGINT          NOT NULL,
  `expense_id`    BIGINT UNSIGNED NULL,
  `note`          VARCHAR(200)    NULL,
  `created_at`    DATETIME        NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_log_user` (`user_id`, `id`),
  CONSTRAINT `fk_log_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Valyuta kurslari keshi (1 USD = ? so'm). O'zbekiston Markaziy banki (CBU) dan olinadi.
CREATE TABLE IF NOT EXISTS `rates` (
  `code`       VARCHAR(8)    NOT NULL,
  `rate`       DECIMAL(16,4) NOT NULL,
  `rate_date`  DATE          NULL,
  `source`     VARCHAR(32)   NOT NULL DEFAULT '',
  `fetched_at` DATETIME      NOT NULL,
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
