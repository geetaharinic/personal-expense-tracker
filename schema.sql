CREATE DATABASE IF NOT EXISTS expense_tracker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE expense_tracker;
CREATE TABLE IF NOT EXISTS transactions (
 id INT AUTO_INCREMENT PRIMARY KEY,
 transaction_date DATE NOT NULL,
 transaction_type VARCHAR(10) NOT NULL,
 category VARCHAR(40) NOT NULL,
 description VARCHAR(200) NOT NULL,
 amount DOUBLE NOT NULL,
 payment_method VARCHAR(30) NOT NULL DEFAULT 'Other',
 created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 INDEX idx_transaction_date (transaction_date)
);
