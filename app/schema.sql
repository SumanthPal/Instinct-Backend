CREATE TABLE IF NOT EXISTS clubs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instagram_handle TEXT UNIQUE NOT NULL,
    club_name TEXT NOT NULL,
    profile_picture TEXT,
    description TEXT,
    followers INTEGER,
    following INTEGER,
    post_count INTEGER
);

-- Create table for posts
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    club_id INTEGER NOT NULL,
    description TEXT,
    date TEXT NOT NULL,
    FOREIGN KEY (club_id) REFERENCES clubs (id) ON DELETE CASCADE
);

-- Create table for parsed events from posts
CREATE TABLE IF NOT EXISTS parsed_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    details TEXT,
    duration_days INTEGER,
    duration_hours INTEGER,
    FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
);

-- Create table for calendar files
CREATE TABLE IF NOT EXISTS calendar_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    club_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    FOREIGN KEY (club_id) REFERENCES clubs (id) ON DELETE CASCADE
)