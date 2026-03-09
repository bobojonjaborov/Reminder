from telebot import types

def delete_reminders_keyboard(reminders):

    markup = types.InlineKeyboardMarkup()

    for reminder in reminders:

        reminder_id, reminder_text, *_ = reminder

        markup.add(
            types.InlineKeyboardButton(
                f"❌ {reminder_text}",
                callback_data=f"delete_{reminder_id}"
            )
        )

    return markup