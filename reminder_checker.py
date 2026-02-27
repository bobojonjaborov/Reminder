import threading
from datetime import datetime, timezone
import time
from crud import mark_as_sent
from db import get_connection


def check_reminders(bot):
    while True:
        current_time = datetime.now(timezone.utc)
        formatted = current_time.strftime("%Y-%m-%d %H:%M:%S")

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, user_id, text, datetime
                FROM reminders
                WHERE datetime <= ?
                AND sent = 0
            """, (formatted,))
            reminders = cursor.fetchall()

        for reminder in reminders:
            reminder_id, user_id, text, reminder_datetime = reminder

            bot.send_message(
                user_id,
                f"⏰ Напоминание:\n{text}"
            )

            mark_as_sent(reminder_id)

        time.sleep(50)


def start_checker(bot):
    thread = threading.Thread(
        target=check_reminders,
        args=(bot,),
        daemon=True
    )
    thread.start()