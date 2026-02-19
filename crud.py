from db import get_connection


def create_reminder(user_id: int, text: str, time: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reminders (user_id, text, time) VALUES (?, ?, ?)",
            (user_id, text, time)
        )
        conn.commit()


def get_user_reminders(user_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, text, time FROM reminders WHERE user_id = ?",
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
