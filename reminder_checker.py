import threading
import datetime
import time
from crud import get_user_reminders, delete_reminder_by_id
from db import get_connection


def check_reminders(bot):
    while True:
        now = datetime.datetime.now().strftime("%H:%M")

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, user_id, text, time FROM reminders WHERE time = ?",
                (now,)
            )
            reminders = cursor.fetchall()

        for reminder in reminders:
            reminder_id, user_id, text, reminder_time = reminder

            bot.send_message(
                user_id,
                f"⏰ Напоминание:\n{text} в {reminder_time}"
            )

            delete_reminder_by_id(reminder_id)

        time.sleep(50)


def start_checker(bot):
    thread = threading.Thread(
        target=check_reminders,
        args=(bot,),
        daemon=True
    )
    thread.start()
