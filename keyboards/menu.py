from telebot import types

def main_menu():
    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton(
        "➕ Добавить напоминание",
        callback_data="add_reminder"
    ))

    markup.add(types.InlineKeyboardButton(
        "📋 Список напоминаний",
        callback_data="list"
    ))

    markup.add(types.InlineKeyboardButton(
        "❌ Удалить все напоминания",
        callback_data="delete_all"
    ))

    markup.add(types.InlineKeyboardButton(
        "❌ Удалить напоминание",
        callback_data="delete_menu"
    ))

    markup.add(types.InlineKeyboardButton(
        "⚙ Установить часовой пояс",
        callback_data="set_timezone"
    ))

    return markup


def back_to_menu_keyboard():

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "⬅ Главное меню",
            callback_data="main_menu"
        )
    )

    return markup