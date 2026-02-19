from crud import create_reminder, get_user_reminders, delete_user_reminders
from states import UserState
from crud import create_reminder

user_states = {}
temp_data = {}


def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def main(message):
        bot.send_message(
            message.chat.id,
            '/add_reminder - <b>Добавить напоминание</b> \n/list - <b>Список напоминаний</b> \n/delete_all - <b>Удалить все напоминания</b>',
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

            import datetime
            try:
                parsed_time = datetime.datetime.strptime(time_text, "%H:%M")
                formatted_time = parsed_time.strftime("%H:%M")

                create_reminder(user_id, temp_data[user_id], formatted_time)

                bot.send_message(message.chat.id, "Напоминание сохранено!")

                del user_states[user_id]
                del temp_data[user_id]

            except ValueError:
                bot.send_message(message.chat.id, "Неверный формат времени. Попробуй ещё раз.")

