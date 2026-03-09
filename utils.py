from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from datetime import datetime, timedelta, timezone
from crud import get_user_reminders
from keyboards.menu import back_to_menu_keyboard

def is_valid_timezone(tz_text: str):
    try:
        ZoneInfo(tz_text)
        return True
    except ZoneInfoNotFoundError:
        return False


def build_reminder_datetime(time_text: str, user_timezone):
    user_tz = ZoneInfo(user_timezone)

    parsed_time = datetime.strptime(time_text, "%H:%M")

    now_local = datetime.now(user_tz)

    reminder_local = now_local.replace(
        hour=parsed_time.hour,
        minute=parsed_time.minute,
        second=0,
        microsecond=0
    )

    if reminder_local <= now_local:
        reminder_local += timedelta(days=1)

    reminder_utc = reminder_local.astimezone(timezone.utc)

    return reminder_utc.strftime("%Y-%m-%d %H:%M:%S")

def send_reminders_list(bot, call):
    reminders = get_user_reminders(call.from_user.id)

    if not reminders:
        bot.edit_message_text(
            "У вас нет напоминаний",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=back_to_menu_keyboard()
        )
        return

    text = "Ваши напоминания:\n\n"

    for i, reminder in enumerate(reminders, start=1):

        reminder_id, reminder_text, reminder_datetime, user_timezone = reminder

        reminder_utc = datetime.strptime(
            reminder_datetime, "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=timezone.utc)

        user_tz = ZoneInfo(user_timezone)
        local_time = reminder_utc.astimezone(user_tz)

        formatted_time = local_time.strftime("%Y-%m-%d %H:%M")

        text += f"{i}. {reminder_text} — {formatted_time}\n"

    bot.edit_message_text(
        text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=back_to_menu_keyboard()
    )

