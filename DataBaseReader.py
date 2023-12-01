import sqlite3

conn = sqlite3.connect('bot.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    number INTEGER NOT NULL,
    email TEXT,
    chat_id TEXT NOT NULL,
    isAdmin INTEGER NOT NULL,
    isManager INTEGER NOT NULL
);
""")