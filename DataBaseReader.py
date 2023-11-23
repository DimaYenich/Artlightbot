import sqlite3

conn = sqlite3.connect('bot.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Customers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    number INTEGER NOT NULL,
    email TEXT,
    chat_id TEXT NOT NULL
);
""")