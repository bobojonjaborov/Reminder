import threading
from datetime import datetime, timezone
import time
from crud import mark_as_sent, reminders_to_send
from zoneinfo import ZoneInfo


def check_reminders(bot):
    while True:
        current_time = datetime.now(timezone.utc)
        formatted = current_time.strftime("%Y-%m-%d %H:%M:%S")

        reminders = reminders_to_send(formatted)

        for reminder in reminders:
            reminder_id, user_id, text, reminder_datetime, user_timezone = reminder

            reminder_utc = datetime.strptime(reminder_datetime, "%Y-%m-%d %H:%M:%S")
            reminder_utc = reminder_utc.replace(tzinfo=timezone.utc)

            user_tz = ZoneInfo(user_timezone)
            local_time = reminder_utc.astimezone(user_tz)

            bot.send_message(
                user_id,
                f"⏰ Напоминание:\n{text} в {local_time.strftime('%H:%M')}"
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