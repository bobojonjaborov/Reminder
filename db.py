import sqlite3

DB_NAME = "reminders.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            datetime TEXT NOT NULL,
            sent INTEGER NOT NULL DEFAULT 0
        )
        """)

        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            timezone TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reminders_datetime_sent
        ON reminders(datetime, sent)
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reminders_user_id
        ON reminders(user_id)
        """)
        conn.commit()