-- =============================================================================
-- Finance Tracker — MySQL Schema
-- =============================================================================
-- Run this file if you prefer to create tables manually instead of letting
-- SQLAlchemy auto-create them on startup.
--
-- Usage:
--   mysql -u root -p < scripts/schema.sql
-- =============================================================================

CREATE DATABASE IF NOT EXISTS finance_tracker
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE finance_tracker;

-- ── Users table ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    user_id    INT          NOT NULL AUTO_INCREMENT,
    full_name  VARCHAR(100) NOT NULL,
    email      VARCHAR(150) NOT NULL,
    hashed_pw  VARCHAR(255) NOT NULL,
    role       ENUM('admin', 'analyst', 'viewer') NOT NULL DEFAULT 'viewer',
    is_active  TINYINT(1)   NOT NULL DEFAULT 1,
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id),
    UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── Financial records table ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS financial_records (
    record_id  INT     NOT NULL AUTO_INCREMENT,
    amount     DOUBLE  NOT NULL,
    txn_type   ENUM('income', 'expense') NOT NULL,
    category   ENUM(
        'salary', 'freelance', 'investment',
        'food', 'transport', 'housing', 'healthcare',
        'education', 'shopping', 'utilities',
        'travel', 'entertainment', 'other'
    ) NOT NULL,
    txn_date   DATE     NOT NULL,
    notes      TEXT,
    owner_id   INT      NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (record_id),
    INDEX ix_financial_records_owner  (owner_id),
    INDEX ix_financial_records_date   (txn_date),
    INDEX ix_financial_records_type   (txn_type),

    CONSTRAINT fk_records_user
        FOREIGN KEY (owner_id)
        REFERENCES users (user_id)
        ON DELETE CASCADE   -- deleting a user removes all their records too
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
