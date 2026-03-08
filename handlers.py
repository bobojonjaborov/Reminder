from crud import (get_user_reminders, delete_user_reminders, delete_reminder_by_id, get_user_timezone, save_user_timezone,
                  delete_user_timezone, create_reminder)
from states import UserState
from utils import is_valid_timezone, build_reminder_datetime
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo


user_states = {}
temp_data = {}


def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def main(message):
        user_id = message.from_user.id
        tz = get_user_timezone(user_id)
        if tz is None:
            user_states[user_id] = UserState.WAITING_TIMEZONE
            bot.send_message(message.chat.id, 'Введите ваш часовой пояс и перезепустите бот. \nПример: Asia/Dushanbe')

        else:
            bot.send_message(
                message.chat.id,
                '/set_timezone - <b>Добавить часовой пояс</b>\n'
                '/add_reminder - <b>Добавить напоминание</b>\n'
                '/list - <b>Список напоминаний</b>\n'
                '/delete_all - <b>Удалить все напоминания</b>\n'
                '/delete &lt;номер&gt; - <b>Удалить напоминание по номеру</b>',
                parse_mode='HTML'

            )


    @bot.message_handler(commands=['set_timezone'])
    def set_timezone(message):
        user_id = message.from_user.id

        user_states[user_id] = UserState.WAITING_TIMEZONE
        bot.send_message(message.chat.id, 'Введите ваш часовой пояс: \n(Asia/Dushanbe)')


    @bot.message_handler(commands=['list'])
    def list_reminders(message):
        user_id = message.from_user.id
        reminders = get_user_reminders(user_id)

        if not reminders:
            bot.send_message(message.chat.id, "Список напоминаний пуст!")
            return

        text = ""

        for i, reminder in enumerate(reminders, start=1):
            reminder_id, reminder_text, reminder_datetime, user_timezone = reminder

            reminder_utc = datetime.strptime(reminder_datetime, "%Y-%m-%d %H:%M:%S")
            reminder_utc = reminder_utc.replace(tzinfo=timezone.utc)

            user_tz = ZoneInfo(user_timezone)
            local_time = reminder_utc.astimezone(user_tz)

            today = datetime.now(user_tz).date()

            if local_time.date() == today:
                date_text = "сегодня"
            elif local_time.date() == today + timedelta(days=1):
                date_text = "завтра"
            else:
                date_text = local_time.strftime("%d.%m")

            text += f"{i}. {reminder_text} — {date_text} в {local_time.strftime('%H:%M')}\n"

        bot.send_message(message.chat.id, text)


    @bot.message_handler(commands=['delete_all'])
    def delete_all(message):
        user_id = message.from_user.id
        delete_user_reminders(user_id)
        bot.send_message(message.chat.id, "Ваши напоминания удалены!")


    @bot.message_handler(commands=['delete_tz'])
    def delete_tz(message):
        user_id = message.from_user.id
        delete_user_timezone(user_id)
        bot.send_message(message.chat.id, "Ваш часовой пояс удалён.")


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
        user_timezone = get_user_timezone(user_id)

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

                formatted_time = build_reminder_datetime(time_text, user_timezone)
                create_reminder(user_id, temp_data[user_id], formatted_time)
                bot.send_message(message.chat.id, "Напоминание сохранено!")

                del user_states[user_id]
                del temp_data[user_id]

            except ValueError:
                bot.send_message(message.chat.id, "Неверный формат времени. Попробуй ещё раз.")

        elif state == UserState.WAITING_TIMEZONE:
            tz_text = message.text.strip()
            is_valid = is_valid_timezone(tz_text)

            if is_valid:
                save_user_timezone(user_id, tz_text)
                del user_states[user_id]
                bot.send_message(message.chat.id, 'Часовой пояс успешно сохранён.')
            else:
                bot.send_message(message.chat.id, 'Неверный часовой пояс. Попробуй ещё раз.')

