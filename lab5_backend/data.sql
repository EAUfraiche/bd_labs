-- ============================================================
-- Лабораторна робота №3. БД "Spotify" (MySQL)
-- ============================================================
-- Аналіз структури (3НФ, Primary Key):
--  * Усі 11 таблиць мають PRIMARY KEY (6 суррогатних AUTO_INCREMENT,
--    2 складені PK у таблицях зв'язку M:N: track_artists, playlist_tracks).
--  * 1НФ: усі атрибути атомарні, повторюваних груп немає.
--  * 2НФ: у таблицях зі складеним PK (track_artists, playlist_tracks)
--    неключові атрибути (role; added_at, position) залежать від усього ключа.
--  * 3НФ: транзитивних залежностей немає — дані про лейбл, жанр,
--    альбом, виконавця винесені в окремі таблиці та підключаються через FK.
--    Поля play_count та monthly_listeners — це збережена статистика,
--    а не похідні від неключових атрибутів, тому 3НФ не порушують.
--  * Зв'язки: label 1:N album, album 1:N track, genre 1:N track,
--    track M:N artist, user 1:N playlist, playlist M:N track,
--    user 1:N device, user 1:1 current_playback.
-- ============================================================

CREATE DATABASE IF NOT EXISTS spotify_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE spotify_db;

-- Видалення таблиць у порядку, зворотному до залежностей (від дочірніх до батьківських)
DROP TABLE IF EXISTS current_playback;
DROP TABLE IF EXISTS devices;
DROP TABLE IF EXISTS playlist_tracks;
DROP TABLE IF EXISTS playlists;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS track_artists;
DROP TABLE IF EXISTS tracks;
DROP TABLE IF EXISTS albums;
DROP TABLE IF EXISTS artists;
DROP TABLE IF EXISTS genres;
DROP TABLE IF EXISTS record_labels;

-- ============================================================
-- СТВОРЕННЯ ТАБЛИЦЬ
-- ============================================================

-- 1. Музичні лейбли
CREATE TABLE record_labels (
    label_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    country VARCHAR(100),
    established_year INT,
    CONSTRAINT uq_record_label_name UNIQUE (name)
) ENGINE=InnoDB;

-- 2. Жанри
CREATE TABLE genres (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    description TEXT,
    CONSTRAINT uq_genre_name UNIQUE (name)
) ENGINE=InnoDB;

-- 3. Виконавці
CREATE TABLE artists (
    artist_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    country VARCHAR(100),
    bio TEXT,
    monthly_listeners BIGINT DEFAULT 0
) ENGINE=InnoDB;

-- 4. Альбоми
CREATE TABLE albums (
    album_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    release_date DATE NOT NULL,
    album_type ENUM('Album', 'Single', 'EP') NOT NULL DEFAULT 'Album',
    label_id INT,
    CONSTRAINT fk_albums_label FOREIGN KEY (label_id)
        REFERENCES record_labels(label_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 5. Треки
CREATE TABLE tracks (
    track_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(250) NOT NULL,
    duration_seconds INT NOT NULL,
    isrc_code VARCHAR(15) NOT NULL,
    album_id INT NOT NULL,
    genre_id INT,
    play_count BIGINT DEFAULT 0,
    CONSTRAINT uq_track_isrc UNIQUE (isrc_code),
    CONSTRAINT fk_tracks_album FOREIGN KEY (album_id)
        REFERENCES albums(album_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_tracks_genre FOREIGN KEY (genre_id)
        REFERENCES genres(genre_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 6. Зв'язок Треки-Виконавці (M:N)
CREATE TABLE track_artists (
    track_id INT NOT NULL,
    artist_id INT NOT NULL,
    role ENUM('Primary', 'Featured', 'Producer') DEFAULT 'Primary',
    PRIMARY KEY (track_id, artist_id),
    CONSTRAINT fk_ta_track FOREIGN KEY (track_id)
        REFERENCES tracks(track_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ta_artist FOREIGN KEY (artist_id)
        REFERENCES artists(artist_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 7. Користувачі
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL,
    email VARCHAR(150) NOT NULL,
    subscription_plan ENUM('Free', 'Premium', 'Family', 'Student') DEFAULT 'Free',
    country VARCHAR(100) DEFAULT 'Ukraine',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_username UNIQUE (username),
    CONSTRAINT uq_user_email UNIQUE (email)
) ENGINE=InnoDB;

-- 8. Плейлисти
CREATE TABLE playlists (
    playlist_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    description VARCHAR(255),
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    CONSTRAINT fk_playlists_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 9. Треки в плейлистах (M:N)
CREATE TABLE playlist_tracks (
    playlist_id INT NOT NULL,
    track_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    position INT NOT NULL,
    PRIMARY KEY (playlist_id, track_id),
    CONSTRAINT fk_pt_playlist FOREIGN KEY (playlist_id)
        REFERENCES playlists(playlist_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_pt_track FOREIGN KEY (track_id)
        REFERENCES tracks(track_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 10. Пристрої користувачів
CREATE TABLE devices (
    device_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    device_name VARCHAR(100) NOT NULL,
    device_type ENUM('Smartphone', 'Desktop', 'Tablet', 'SmartSpeaker', 'TV') NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_devices_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 11. Поточне відтворення (1:1 з користувачем)
CREATE TABLE current_playback (
    playback_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    track_id INT NOT NULL,
    device_id INT,
    progress_seconds INT DEFAULT 0,
    is_playing BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_playback_user UNIQUE (user_id),
    CONSTRAINT fk_playback_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_playback_track FOREIGN KEY (track_id)
        REFERENCES tracks(track_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_playback_device FOREIGN KEY (device_id)
        REFERENCES devices(device_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- ДОДАТКОВІ ІНДЕКСИ (за результатами аналізу типових запитів)
-- ============================================================
-- Пошук треків / виконавців / плейлистів за назвою
CREATE INDEX idx_tracks_title ON tracks(title);
CREATE INDEX idx_artists_name ON artists(name);
CREATE INDEX idx_playlists_title ON playlists(title);
-- Вибірка нових релізів, сортування за датою
CREATE INDEX idx_albums_release_date ON albums(release_date);
-- Топ-чарти за кількістю прослуховувань
CREATE INDEX idx_tracks_play_count ON tracks(play_count);
-- Фільтрація користувачів за країною та тарифом
CREATE INDEX idx_users_country_plan ON users(country, subscription_plan);

-- ============================================================
-- НАПОВНЕННЯ ДАНИМИ (порядок: спочатку батьківські таблиці)
-- ============================================================

-- 1. record_labels (10)
INSERT INTO record_labels (label_id, name, country, established_year) VALUES
(1, 'Universal Music Group', 'USA', 1934),
(2, 'Sony Music Entertainment', 'USA', 1929),
(3, 'Warner Music Group', 'USA', 1958),
(4, 'Enko', 'Ukraine', 2020),
(5, 'Moon Records', 'Ukraine', 1997),
(6, 'XO Records', 'Canada', 2012),
(7, 'Parlophone', 'UK', 1896),
(8, 'Columbia Records', 'USA', 1887),
(9, 'Republic Records', 'USA', 1995),
(10, 'Atlantic Records', 'USA', 1947);

-- 2. genres (10)
INSERT INTO genres (genre_id, name, description) VALUES
(1, 'Hip-Hop', 'Urban music focusing on rhythmic beats and rhyming'),
(2, 'Rock', 'Classic and contemporary rock rhythms and electric guitars'),
(3, 'Pop', 'Mainstream popular music with catchy melodies'),
(4, 'Electronic', 'Synthesizer and digital production driven tracks'),
(5, 'Indie', 'Independent and alternative music'),
(6, 'Folk', 'Traditional ethnic musical motifs combined with modern sounds'),
(7, 'R&B', 'Rhythm and blues with soulful vocals'),
(8, 'Jazz', 'Improvisation-based music with swing and blue notes'),
(9, 'Classical', 'Orchestral and chamber compositions'),
(10, 'Metal', 'Heavy, distorted guitars and aggressive vocals');

-- 3. artists (10)
INSERT INTO artists (artist_id, name, country, bio, monthly_listeners) VALUES
(1, 'The Weeknd', 'Canada', 'Canadian singer, songwriter, and record producer', 105000000),
(2, 'Daft Punk', 'France', 'Legendary French electronic music duo', 25000000),
(3, 'Kalush Orchestra', 'Ukraine', 'Ukrainian folk-hip-hop band, Eurovision 2022 winners', 3200000),
(4, 'Linkin Park', 'USA', 'Iconic alternative rock and nu-metal band', 42000000),
(5, 'Dua Lipa', 'UK', 'English and Albanian pop superstar', 78000000),
(6, 'Okean Elzy', 'Ukraine', 'Famous Ukrainian rock band led by Svyatoslav Vakarchuk', 1900000),
(7, 'Billie Eilish', 'USA', 'American singer-songwriter known for whispery vocals', 85000000),
(8, 'Imagine Dragons', 'USA', 'American pop rock band from Las Vegas', 60000000),
(9, 'Jamala', 'Ukraine', 'Ukrainian singer, Eurovision 2016 winner', 1500000),
(10, 'Tame Impala', 'Australia', 'Psychedelic project of Kevin Parker', 30000000);

-- 4. albums (12)
INSERT INTO albums (album_id, title, release_date, album_type, label_id) VALUES
(1, 'After Hours', '2020-03-20', 'Album', 1),
(2, 'Random Access Memories', '2013-05-17', 'Album', 2),
(3, 'Stefania', '2022-02-07', 'Single', 4),
(4, 'Meteora', '2003-03-25', 'Album', 3),
(5, 'Future Nostalgia', '2020-03-27', 'Album', 3),
(6, 'Zemlya', '2013-05-15', 'Album', 5),
(7, 'Hit Me Hard and Soft', '2024-05-17', 'Album', 1),
(8, 'Evolve', '2017-06-23', 'Album', 9),
(9, '1944', '2016-02-12', 'Single', 5),
(10, 'Currents', '2015-07-17', 'Album', 8),
(11, 'Starboy', '2016-11-25', 'Album', 6),
(12, 'Hybrid Theory', '2000-10-24', 'Album', 3);

-- 5. tracks (15)
INSERT INTO tracks (track_id, title, duration_seconds, isrc_code, album_id, genre_id, play_count) VALUES
(1, 'Blinding Lights', 200, 'USUG12000412', 1, 3, 4200000000),
(2, 'Save Your Tears', 215, 'USUG12000415', 1, 3, 1900000000),
(3, 'Get Lucky', 369, 'FRZ031300001', 2, 4, 1100000000),
(4, 'Instant Crush', 337, 'FRZ031300005', 2, 4, 650000000),
(5, 'Stefania', 179, 'UAEN12200001', 3, 6, 95000000),
(6, 'Numb', 187, 'USWB10300045', 4, 2, 1750000000),
(7, 'Levitating', 203, 'GBAHT2000123', 5, 3, 2100000000),
(8, 'Obimy', 224, 'UAMO11300021', 6, 2, 120000000),
(9, 'Starboy', 230, 'USUG11601234', 11, 7, 3000000000),
(10, 'Birds of a Feather', 210, 'USUG12400101', 7, 3, 1500000000),
(11, 'Believer', 204, 'USUM71700123', 8, 2, 2400000000),
(12, 'Thunder', 187, 'USUM71700124', 8, 5, 2200000000),
(13, '1944', 267, 'UAMO11600001', 9, 6, 70000000),
(14, 'The Less I Know the Better', 216, 'AUUM71500123', 10, 5, 1800000000),
(15, 'In the End', 216, 'USWB10000987', 12, 2, 2900000000);

-- 6. track_artists (15)
INSERT INTO track_artists (track_id, artist_id, role) VALUES
(1, 1, 'Primary'),
(2, 1, 'Primary'),
(3, 2, 'Primary'),
(4, 2, 'Primary'),
(5, 3, 'Primary'),
(6, 4, 'Primary'),
(7, 5, 'Primary'),
(8, 6, 'Primary'),
(9, 1, 'Primary'),
(10, 7, 'Primary'),
(11, 8, 'Primary'),
(12, 8, 'Primary'),
(13, 9, 'Primary'),
(14, 10, 'Primary'),
(15, 4, 'Primary');

-- 7. users (10)
INSERT INTO users (user_id, username, email, subscription_plan, country) VALUES
(1, 'taras_fok', 'taras.f@gmail.com', 'Premium', 'Ukraine'),
(2, 'alex_dev', 'alex.developer@tech.io', 'Free', 'Poland'),
(3, 'olena_m', 'olena.music@ukr.net', 'Student', 'Ukraine'),
(4, 'john_doe', 'john.doe@example.com', 'Family', 'USA'),
(5, 'marta_k', 'marta.koval@gmail.com', 'Premium', 'Ukraine'),
(6, 'ivan_p', 'ivan.petrenko@gmail.com', 'Free', 'Ukraine'),
(7, 'sofia_l', 'sofia.lysenko@ukr.net', 'Student', 'Ukraine'),
(8, 'max_b', 'max.bauer@web.de', 'Premium', 'Germany'),
(9, 'anna_v', 'anna.v@example.com', 'Family', 'Canada'),
(10, 'dmytro_h', 'dmytro.h@gmail.com', 'Free', 'Ukraine');

-- 8. playlists (10)
INSERT INTO playlists (playlist_id, title, description, is_public, user_id) VALUES
(1, 'Coding Focus Beats', 'Instrumental and synthwave tracks for programming', TRUE, 1),
(2, 'Workout Energy', 'Heavy rock and upbeat tracks for gym', TRUE, 1),
(3, 'Chill Ukrainian Vibes', 'Modern and folk Ukrainian music', TRUE, 3),
(4, 'Road Trip 2026', 'Best songs for long driving trips', FALSE, 4),
(5, 'Top Global Hits', 'Radio favorites from Dua Lipa and The Weeknd', TRUE, 5),
(6, 'Morning Coffee', 'Soft indie for a calm start of the day', TRUE, 6),
(7, 'Rock Classics', 'Timeless rock and nu-metal anthems', TRUE, 7),
(8, 'Party Mix', 'Dance and R&B hits for the weekend', FALSE, 8),
(9, 'Study Session', 'Background music for studying', TRUE, 9),
(10, 'Evening Relax', 'Slow tracks to unwind after work', FALSE, 10);

-- 9. playlist_tracks (15)
INSERT INTO playlist_tracks (playlist_id, track_id, position) VALUES
(1, 3, 1),
(1, 4, 2),
(2, 6, 1),
(2, 1, 2),
(3, 5, 1),
(3, 8, 2),
(4, 1, 1),
(5, 7, 1),
(5, 10, 2),
(6, 14, 1),
(7, 6, 1),
(7, 15, 2),
(8, 9, 1),
(9, 11, 1),
(10, 13, 1);

-- 10. devices (12)
INSERT INTO devices (device_id, user_id, device_name, device_type, is_active) VALUES
(1, 1, 'Ubuntu Workstation', 'Desktop', TRUE),
(2, 1, 'Samsung Galaxy S24', 'Smartphone', FALSE),
(3, 2, 'MacBook Air M2', 'Desktop', TRUE),
(4, 3, 'iPhone 15 Pro', 'Smartphone', TRUE),
(5, 4, 'Living Room Echo', 'SmartSpeaker', TRUE),
(6, 5, 'iPad Air', 'Tablet', FALSE),
(7, 6, 'Samsung Smart TV', 'TV', TRUE),
(8, 7, 'Google Pixel 8', 'Smartphone', TRUE),
(9, 8, 'Gaming PC', 'Desktop', FALSE),
(10, 9, 'Kitchen Speaker', 'SmartSpeaker', TRUE),
(11, 10, 'Lenovo Tab M10', 'Tablet', FALSE),
(12, 3, 'Work Laptop', 'Desktop', FALSE);

-- 11. current_playback (10)
INSERT INTO current_playback (user_id, track_id, device_id, progress_seconds, is_playing) VALUES
(1, 3, 1, 120, TRUE),
(2, 1, 3, 45, TRUE),
(3, 5, 4, 110, TRUE),
(4, 7, 5, 30, FALSE),
(5, 8, NULL, 0, FALSE),
(6, 14, 7, 60, TRUE),
(7, 11, 8, 150, TRUE),
(8, 9, 9, 10, FALSE),
(9, 13, 10, 200, TRUE),
(10, 2, 11, 95, FALSE);
