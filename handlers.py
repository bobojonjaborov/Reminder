from crud import (get_user_reminders, delete_user_reminders, delete_reminder_by_id, get_user_timezone, save_user_timezone,
                  delete_user_timezone, create_reminder)
from states import UserState
from utils import is_valid_timezone, build_reminder_datetime, send_reminders_list
from keyboards.menu import main_menu, back_to_menu_keyboard
from keyboards.delete_menu import delete_reminders_keyboard


user_states = {}
temp_data = {}


def register_handlers(bot):
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callbacks(call):

        bot.answer_callback_query(call.id)

        if call.data == "add_reminder":
            user_id = call.from_user.id
            user_states[user_id] = UserState.WAITING_TEXT

            bot.send_message(call.message.chat.id, "Что вам напомнить?")

        elif call.data == "delete_all":

            user_id = call.from_user.id

            delete_user_reminders(user_id)

            bot.edit_message_text(
                "Все напоминания удалены",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=back_to_menu_keyboard()
            )

        elif call.data == "delete_menu":

            user_id = call.from_user.id
            reminders = get_user_reminders(user_id)

            if not reminders:
                bot.send_message(
                    call.message.chat.id,
                    "У вас нет напоминаний",
                    reply_markup=back_to_menu_keyboard()
                )
                return

            keyboard = delete_reminders_keyboard(reminders)

            bot.edit_message_text(
                "Выберите напоминание для удаления",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard
            )

        elif call.data.startswith("delete_"):

            reminder_id = int(call.data.split("_")[-1])

            delete_reminder_by_id(reminder_id)

            bot.edit_message_text(
                "Напоминание удалено",
                message_id=call.message.message_id,
                chat_id=call.message.chat.id,
                reply_markup=back_to_menu_keyboard()
            )

        elif call.data == "main_menu":
            bot.edit_message_text(
                "🔔 Reminder Bot\n\nВыберите действие:",
                message_id=call.message.message_id,
                chat_id=call.message.chat.id,
                reply_markup=main_menu()
            )

        elif call.data == "list":
            send_reminders_list(bot, call)


        elif call.data == "set_timezone":
            user_id = call.from_user.id

            user_states[user_id] = UserState.WAITING_TIMEZONE

            bot.send_message(
                call.message.chat.id,
                "Введите ваш часовой пояс\n\nПример: Asia/Dushanbe"
            )

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
                "🔔 Reminder Bot\n\nВыберите действие:",
                reply_markup=main_menu()
            )

    @bot.message_handler(commands=['set_timezone'])
    def set_timezone(message):
        user_id = message.from_user.id

        user_states[user_id] = UserState.WAITING_TIMEZONE
        bot.send_message(message.chat.id, 'Введите ваш часовой пояс: \n(Asia/Dushanbe)')


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
                bot.send_message(message.chat.id, "Напоминание сохранено!", reply_markup=main_menu())

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
                bot.send_message(message.chat.id, 'Часовой пояс успешно сохранён.', reply_markup=back_to_menu_keyboard())
            else:
                bot.send_message(message.chat.id, 'Неверный часовой пояс. Попробуй ещё раз.')