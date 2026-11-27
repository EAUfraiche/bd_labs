-- =====================================================================
-- Лабораторна робота №5. Stored programs in MySQL (БД spotify_db)
-- Спершу виконайте data.sql (створення БД), потім цей файл:
--   mysql -u root -p < lab5.sql
-- =====================================================================
USE spotify_db;

-- ---------------------------------------------------------------------
-- Очищення (щоб скрипт можна було запускати повторно)
-- ---------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_reviews_bi;
DROP TRIGGER IF EXISTS trg_reviews_bu;
DROP TRIGGER IF EXISTS trg_tracks_bd_reviews;
DROP TRIGGER IF EXISTS trg_tracks_bu_reviews;
DROP TRIGGER IF EXISTS trg_users_bi_letter;
DROP TRIGGER IF EXISTS trg_users_bu_letter;
DROP TRIGGER IF EXISTS trg_playlists_ad_log;
DROP TRIGGER IF EXISTS trg_tracks_bi_duration;
DROP TRIGGER IF EXISTS trg_tracks_bu_duration;
DROP PROCEDURE IF EXISTS sp_insert_artist;
DROP PROCEDURE IF EXISTS sp_add_track_artist;
DROP PROCEDURE IF EXISTS sp_insert_noname_batch;
DROP PROCEDURE IF EXISTS sp_duration_stat;
DROP PROCEDURE IF EXISTS sp_split_artists_random;
DROP FUNCTION IF EXISTS fn_duration_stat;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS playlists_delete_log;

-- =====================================================================
-- 1. Нова таблиця reviews зі зв'язком 1:M до tracks БЕЗ фізичного FOREIGN KEY.
--    Цілісність забезпечують тригери (див. нижче).
-- =====================================================================
CREATE TABLE reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    track_id  INT NOT NULL,                       -- логічне посилання на tracks.track_id
    reviewer  VARCHAR(80) NOT NULL,
    rating    TINYINT NOT NULL,
    comment   VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_reviews_rating CHECK (rating BETWEEN 1 AND 5),
    INDEX idx_reviews_track (track_id)
) ENGINE=InnoDB;

-- Журнал видалених плейлистів (для тригера 3.f)
CREATE TABLE playlists_delete_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    playlist_id INT,
    title VARCHAR(150),
    user_id INT,
    deleted_by VARCHAR(100),
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

DELIMITER $$

-- ---------------------------------------------------------------------
-- 1. Тригери, що замінюють FOREIGN KEY reviews.track_id -> tracks.track_id
-- ---------------------------------------------------------------------
-- (дочірня таблиця) не можна вставити відгук на неіснуючий трек
CREATE TRIGGER trg_reviews_bi BEFORE INSERT ON reviews
FOR EACH ROW
BEGIN
    IF NOT EXISTS (SELECT 1 FROM tracks WHERE track_id = NEW.track_id) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Integrity error: track_id does not exist in tracks';
    END IF;
END$$

-- (дочірня таблиця) не можна перенести відгук на неіснуючий трек
CREATE TRIGGER trg_reviews_bu BEFORE UPDATE ON reviews
FOR EACH ROW
BEGIN
    IF NOT EXISTS (SELECT 1 FROM tracks WHERE track_id = NEW.track_id) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Integrity error: track_id does not exist in tracks';
    END IF;
END$$

-- (батьківська таблиця) не можна видалити трек, у якого є відгуки (RESTRICT)
CREATE TRIGGER trg_tracks_bd_reviews BEFORE DELETE ON tracks
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT 1 FROM reviews WHERE track_id = OLD.track_id) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Integrity error: track has reviews and cannot be deleted';
    END IF;
END$$

-- (батьківська таблиця) не можна змінити track_id треку, у якого є відгуки
CREATE TRIGGER trg_tracks_bu_reviews BEFORE UPDATE ON tracks
FOR EACH ROW
BEGIN
    IF NEW.track_id <> OLD.track_id
       AND EXISTS (SELECT 1 FROM reviews WHERE track_id = OLD.track_id) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Integrity error: track has reviews, track_id cannot be changed';
    END IF;
END$$

DELIMITER ;

-- Тестові відгуки (тригери вже перевіряють track_id)
INSERT INTO reviews (track_id, reviewer, rating, comment) VALUES
(1,  'taras_fok', 5, 'Great synth vibes'),
(3,  'olena_m',   4, 'A modern classic'),
(6,  'john_doe',  5, 'Nostalgic'),
(9,  'marta_k',   3, 'Okay'),
(11, 'ivan_p',    4, 'Energetic');

DELIMITER $$

-- =====================================================================
-- 3. Три довільні тригери (за прикладами з завдання)
-- =====================================================================
-- 3.k  Перша літера username має збігатися з першою літерою сусіднього поля email
CREATE TRIGGER trg_users_bi_letter BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    IF LOWER(LEFT(NEW.username, 1)) <> LOWER(LEFT(NEW.email, 1)) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'First letter of username must match first letter of email';
    END IF;
END$$

CREATE TRIGGER trg_users_bu_letter BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    IF LOWER(LEFT(NEW.username, 1)) <> LOWER(LEFT(NEW.email, 1)) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'First letter of username must match first letter of email';
    END IF;
END$$

-- 3.f  Журнал зі штампом часу при видаленні даних з playlists
CREATE TRIGGER trg_playlists_ad_log AFTER DELETE ON playlists
FOR EACH ROW
BEGIN
    INSERT INTO playlists_delete_log (playlist_id, title, user_id, deleted_by)
    VALUES (OLD.playlist_id, OLD.title, OLD.user_id, CURRENT_USER());
END$$

-- 3.a  Значення tracks.duration_seconds не може закінчуватися двома нулями
CREATE TRIGGER trg_tracks_bi_duration BEFORE INSERT ON tracks
FOR EACH ROW
BEGIN
    IF MOD(NEW.duration_seconds, 100) = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'duration_seconds must not end with two zeros';
    END IF;
END$$

CREATE TRIGGER trg_tracks_bu_duration BEFORE UPDATE ON tracks
FOR EACH ROW
BEGIN
    IF NEW.duration_seconds <> OLD.duration_seconds
       AND MOD(NEW.duration_seconds, 100) = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'duration_seconds must not end with two zeros';
    END IF;
END$$

-- =====================================================================
-- 2.a  Параметризована вставка у таблицю artists
-- =====================================================================
CREATE PROCEDURE sp_insert_artist(
    IN p_name VARCHAR(150),
    IN p_country VARCHAR(100),
    IN p_bio TEXT,
    IN p_listeners BIGINT)
BEGIN
    IF p_name IS NULL OR TRIM(p_name) = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Artist name must not be empty';
    END IF;

    INSERT INTO artists (name, country, bio, monthly_listeners)
    VALUES (TRIM(p_name), p_country, p_bio, IFNULL(p_listeners, 0));

    SELECT * FROM artists WHERE artist_id = LAST_INSERT_ID();
END$$

-- =====================================================================
-- 2.b  Зв'язок M:M: вставка в track_artists за реальними значеннями
--      (назва треку + ім'я виконавця), а не за id
-- =====================================================================
CREATE PROCEDURE sp_add_track_artist(
    IN p_track_title VARCHAR(250),
    IN p_artist_name VARCHAR(150),
    IN p_role VARCHAR(20))
BEGIN
    DECLARE v_track_id INT DEFAULT NULL;
    DECLARE v_artist_id INT DEFAULT NULL;

    SET p_role = IFNULL(p_role, 'Primary');
    IF p_role NOT IN ('Primary', 'Featured', 'Producer') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Role must be Primary, Featured or Producer';
    END IF;

    SELECT track_id INTO v_track_id FROM tracks
     WHERE title = p_track_title ORDER BY track_id LIMIT 1;
    SELECT artist_id INTO v_artist_id FROM artists
     WHERE name = p_artist_name ORDER BY artist_id LIMIT 1;

    IF v_track_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Track with this title not found';
    END IF;
    IF v_artist_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Artist with this name not found';
    END IF;

    INSERT INTO track_artists (track_id, artist_id, role)
    VALUES (v_track_id, v_artist_id, p_role)
    ON DUPLICATE KEY UPDATE role = p_role;

    SELECT t.track_id, t.title AS track, a.artist_id, a.name AS artist, ta.role
      FROM track_artists ta
      JOIN tracks t  ON t.track_id  = ta.track_id
      JOIN artists a ON a.artist_id = ta.artist_id
     WHERE ta.track_id = v_track_id AND ta.artist_id = v_artist_id;
END$$

-- =====================================================================
-- 2.c  Пакет: вставка 10 рядків у artists у форматі Noname<№>
--      Нумерація продовжується з найбільшого вже існуючого номера.
-- =====================================================================
CREATE PROCEDURE sp_insert_noname_batch()
BEGIN
    DECLARE v_i INT DEFAULT 1;
    DECLARE v_start INT DEFAULT 0;
    DECLARE v_prev_max INT DEFAULT 0;

    SELECT IFNULL(MAX(artist_id), 0) INTO v_prev_max FROM artists;
    SELECT IFNULL(MAX(CAST(SUBSTRING(name, 7) AS UNSIGNED)), 0) INTO v_start
      FROM artists WHERE name REGEXP '^Noname[0-9]+$';

    START TRANSACTION;
    WHILE v_i <= 10 DO
        INSERT INTO artists (name, country) VALUES (CONCAT('Noname', v_start + v_i), 'Unknown');
        SET v_i = v_i + 1;
    END WHILE;
    COMMIT;

    SELECT artist_id, name FROM artists WHERE artist_id > v_prev_max ORDER BY artist_id;
END$$

-- =====================================================================
-- 2.d  Користувацька функція: Max / Min / Sum / Avg для tracks.duration_seconds
--      і процедура, яка викликає її у SELECT
-- =====================================================================
CREATE FUNCTION fn_duration_stat(p_stat VARCHAR(10))
RETURNS DECIMAL(20,2)
READS SQL DATA
BEGIN
    DECLARE v DECIMAL(20,2) DEFAULT NULL;
    CASE UPPER(p_stat)
        WHEN 'MAX' THEN SELECT MAX(duration_seconds) INTO v FROM tracks;
        WHEN 'MIN' THEN SELECT MIN(duration_seconds) INTO v FROM tracks;
        WHEN 'SUM' THEN SELECT SUM(duration_seconds) INTO v FROM tracks;
        WHEN 'AVG' THEN SELECT AVG(duration_seconds) INTO v FROM tracks;
        ELSE SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stat must be MAX, MIN, SUM or AVG';
    END CASE;
    RETURN v;
END$$

CREATE PROCEDURE sp_duration_stat(IN p_stat VARCHAR(10))
BEGIN
    SELECT UPPER(p_stat) AS stat,
           'tracks.duration_seconds' AS column_name,
           fn_duration_stat(p_stat) AS value;
END$$

-- =====================================================================
-- 2.e (i)  Курсор: динамічно створити 2 таблиці з штампом часу в імені
--          (структура = artists) і випадково розкидати рядки artists
--          між ними. Кожен запуск створює нову пару таблиць.
-- =====================================================================
CREATE PROCEDURE sp_split_artists_random()
BEGIN
    DECLARE v_id INT;
    DECLARE v_done INT DEFAULT 0;
    DECLARE v_c1 INT DEFAULT 0;
    DECLARE v_c2 INT DEFAULT 0;
    DECLARE cur CURSOR FOR SELECT artist_id FROM artists ORDER BY artist_id;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    SET @stamp = DATE_FORMAT(NOW(6), '%Y%m%d_%H%i%S_%f');
    SET @t1 = CONCAT('artists_', @stamp, '_1');
    SET @t2 = CONCAT('artists_', @stamp, '_2');

    SET @sql = CONCAT('CREATE TABLE `', @t1, '` LIKE artists');
    PREPARE st FROM @sql; EXECUTE st; DEALLOCATE PREPARE st;
    SET @sql = CONCAT('CREATE TABLE `', @t2, '` LIKE artists');
    PREPARE st FROM @sql; EXECUTE st; DEALLOCATE PREPARE st;

    SET @sql = CONCAT('INSERT INTO `', @t1, '` SELECT * FROM artists WHERE artist_id = ?');
    PREPARE ins1 FROM @sql;
    SET @sql = CONCAT('INSERT INTO `', @t2, '` SELECT * FROM artists WHERE artist_id = ?');
    PREPARE ins2 FROM @sql;

    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO v_id;
        IF v_done = 1 THEN
            LEAVE read_loop;
        END IF;
        SET @id = v_id;
        IF RAND() < 0.5 THEN
            EXECUTE ins1 USING @id;
            SET v_c1 = v_c1 + 1;
        ELSE
            EXECUTE ins2 USING @id;
            SET v_c2 = v_c2 + 1;
        END IF;
    END LOOP;
    CLOSE cur;

    DEALLOCATE PREPARE ins1;
    DEALLOCATE PREPARE ins2;

    SELECT @t1 AS table_1, v_c1 AS rows_1, @t2 AS table_2, v_c2 AS rows_2, v_c1 + v_c2 AS total;
END$$

DELIMITER ;
