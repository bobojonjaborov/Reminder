from crud import get_user_reminders, delete_user_reminders, delete_reminder_by_id
from states import UserState
from crud import create_reminder
from datetime import datetime, timedelta, timezone


user_states = {}
temp_data = {}

def build_reminder_datetime(time_text: str) -> str:
    # 1. Таймзона пользователя (UTC+5)
    user_tz = timezone(timedelta(hours=5))

    # 2. Парсим HH:MM
    parsed_time = datetime.strptime(time_text, "%H:%M")

    # 3. Текущее локальное время пользователя
    now_local = datetime.now(user_tz)

    # 4. Создаём datetime на сегодня в его таймзоне
    reminder_local = now_local.replace(
        hour=parsed_time.hour,
        minute=parsed_time.minute,
        second=0,
        microsecond=0
    )

    # 5. Если время уже прошло — переносим на завтра
    if reminder_local <= now_local:
        reminder_local += timedelta(days=1)

    # 6. Переводим в UTC
    reminder_utc = reminder_local.astimezone(timezone.utc)

    # 7. Возвращаем строку без tz info
    return reminder_utc.strftime("%Y-%m-%d %H:%M:%S")
def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def main(message):
        bot.send_message(
            message.chat.id,
            '/add_reminder - <b>Добавить напоминание</b>\n'
            '/list - <b>Список напоминаний</b>\n'
            '/delete_all - <b>Удалить все напоминания</b>\n'
            '/delete &lt;номер&gt; - <b>Удалить напоминание по номеру</b>',
            parse_mode='HTML'
        )

    @bot.message_handler(commands=['list'])
    def list_reminders(message):
        user_id = message.from_user.id
        reminders = get_user_reminders(user_id)

        if not reminders:
            bot.send_message(message.chat.id, "Список напоминаний пуст!")
            return

        text = ""
        for i, reminder in enumerate(reminders, start=1):
            text += f"{i}. {reminder[1]} в {reminder[2]}\n"

        bot.send_message(message.chat.id, text)

    @bot.message_handler(commands=['delete_all'])
    def delete_all(message):
        user_id = message.from_user.id
        delete_user_reminders(user_id)
        bot.send_message(message.chat.id, "Ваши напоминания удалены!")

    @bot.message_handler(commands=['add_reminder'])
    def add_reminder(message):
        user_id = message.from_user.id
        user_states[user_id] = UserState.WAITING_TEXT
        bot.send_message(message.chat.id, "Что вам напомнить?")

    @bot.message_handler(commands=['delete'])
    def delete_by_number(message):
        user_id = message.from_user.id
        parts = message.text.split()

        if len(parts) != 2:
            bot.send_message(message.chat.id, "Использование: /delete <номер>")
            return

        try:
            number = int(parts[1])
        except ValueError:
            bot.send_message(message.chat.id, "Номер должен быть числом.")
            return

        reminders = get_user_reminders(user_id)

        if number < 1 or number > len(reminders):
            bot.send_message(message.chat.id, "Неверный номер.")
            return

        reminder_id = reminders[number - 1][0]

        delete_reminder_by_id(reminder_id)

        bot.send_message(message.chat.id, "Напоминание удалено.")

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        user_id = message.from_user.id

        if user_id not in user_states:
            return

        state = user_states[user_id]

        if state == UserState.WAITING_TEXT:
            temp_data[user_id] = message.text
            user_states[user_id] = UserState.WAITING_TIME
            bot.send_message(message.chat.id, "Во сколько? (HH:MM)")


        elif state == UserState.WAITING_TIME:
            time_text = message.text

            try:
                formatted_time = build_reminder_datetime(time_text)
                create_reminder(user_id, temp_data[user_id], formatted_time)
                bot.send_message(message.chat.id, "Напоминание сохранено!")

                del user_states[user_id]
                del temp_data[user_id]

            except ValueError:
                bot.send_message(message.chat.id, "Неверный формат времени. Попробуй ещё раз.")