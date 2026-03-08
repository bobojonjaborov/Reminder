from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from datetime import datetime, timedelta, timezone

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