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
        cursor.execute(
            "SELECT id, text, datetime FROM reminders WHERE user_id = ?",
            (user_id,)
        )
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
            SELECT id, user_id, text, datetime
            FROM reminders
            WHERE datetime <= ?
            AND sent = 0
        """, (current_time,))
        return cursor.fetchall()

def mark_as_sent(reminder_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE reminders SET sent = 1 WHERE id = ?', (reminder_id,))
        conn.commit()