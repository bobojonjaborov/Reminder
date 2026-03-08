from db import get_connection

def create_reminder(user_id: int, text: str, reminder_datetime: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reminders (user_id, text, datetime) VALUES (?, ?, ?)",
            (user_id, text, reminder_datetime)
        )
        conn.commit()


def get_user_reminders(user_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, r.text, r.datetime, u.timezone
            FROM reminders r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.user_id = ?
            ORDER BY r.datetime
            """, (user_id,))
        return cursor.fetchall()


def delete_user_reminders(user_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM reminders WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()


def delete_reminder_by_id(reminder_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM reminders WHERE id = ?",
            (reminder_id,)
        )
        conn.commit()


def reminders_to_send(current_time: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, r.user_id, r.text, r.datetime, u.timezone
            FROM reminders r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.datetime <= ?
            AND r.sent = 0
        """, (current_time,))
        return cursor.fetchall()

def mark_as_sent(reminder_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE reminders SET sent = 1 WHERE id = ?', (reminder_id,))
        conn.commit()

def get_user_timezone(user_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT timezone FROM users WHERE user_id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else None

def delete_user_timezone(user_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM users WHERE user_id = ?',
            (user_id,)
        )
        conn.commit()

def save_user_timezone(user_id: int, tz: str):
    with get_connection() as conn:

        cursor = conn.cursor()
        cursor.execute('SELECT timezone FROM users WHERE user_id = ?', (user_id,))
        exist = cursor.fetchone()

        if exist:
            cursor.execute('UPDATE users SET timezone = ? WHERE user_id = ?',(tz,user_id))
        else:
            cursor.execute('INSERT INTO users (user_id, timezone) VALUES (?, ?)', (user_id, tz))

        conn.commit()