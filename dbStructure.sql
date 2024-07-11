CREATE DATABASE IF NOT EXISTS discordUsers;
--USE discordUsers;

CREATE TABLE IF NOT EXISTS registered (
                          ID INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                          Username VARCHAR(23) NOT NULL,
                          Password VARCHAR(32) NOT NULL,
                          Email VARCHAR(39) NOT NULL,
                          --register_time DATETIME NULL,
                          discord_id INT UNSIGNED NOT NULL
                        )