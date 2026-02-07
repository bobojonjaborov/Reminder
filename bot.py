import sqlite3
from time import sleep
import telebot
import datetime
import threading
from os import getenv

from dotenv import load_dotenv

load_dotenv()
TOKEN = getenv('BOT_TOKEN')

bot = telebot.TeleBot(TOKEN)

db_lock = threading.Lock()

user_state = {}
temp_data = {}
list_state = ''

with sqlite3.connect('.venv/reminders.db') as db:
    c = db.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        time TEXT NOT NULL
    )
    """)
    db.commit()

@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(
        message.chat.id,
        '/add_reminder - <b>Добавить напоминание</b> \n/list - <b>Список напоминаний</b> \n/delete_all - <b>Удалить все напоминания</b>',
        parse_mode='HTML'
        )

@bot.message_handler(commands=['add_reminder'])
def add_reminder(message):
    bot.send_message(message.chat.id,'Что вам напомнить?')
    user_id = message.from_user.id
    user_state[user_id] = 'waiting text'

@bot.message_handler(commands=['list'])
def list_reminders(message):
    user_id = message.from_user.id
    with db_lock:
        con = sqlite3.connect('.venv/reminders.db')
        cursor = con.cursor()

        cursor.execute("""SELECT * FROM reminders WHERE user_id = ?""", (user_id,))
        reminders_list = cursor.fetchall()
        con.close()
    if len(reminders_list) == 0:
        bot.send_message(message.chat.id, 'Список напоминаний пуст!!')
    else:
        i = 1
        message_text = ''
        for reminder in reminders_list:
            message_text += f'{i}. {reminder[2]} в {reminder[3]}\n'
            i += 1
        bot.send_message(message.chat.id, message_text)


@bot.message_handler(commands=['delete_all'])
def delete_all(message):
    with (db_lock):
        con = sqlite3.connect('.venv/reminders.db')
        cursor = con.cursor()

        cursor.execute("""DELETE FROM reminders""")
        con.commit()
        con.close()
    bot.send_message(message.chat.id, 'Напоминания успешно удалены!')

@bot.message_handler()
def message_handler(message):
    user_id = message.from_user.id
    if user_id in user_state and user_state[user_id] == 'waiting text':
        user_text = message.text
        temp_data[user_id] = user_text
        user_state[user_id] = 'waiting time'
        bot.send_message(message.chat.id, 'Во сколько напомнить? (формат HH:MM)?')
    elif user_id in user_state and user_state[user_id] == 'waiting time':
        time_text = message.text
        try:
            utime = datetime.datetime.strptime(time_text, "%H:%M")
            user_time = utime.strftime("%H:%M")
            with db_lock:
                con = sqlite3.connect('.venv/reminders.db')
                cursor = con.cursor()

                cursor.execute("INSERT INTO reminders (user_id, text, time) VALUES (?, ?, ?)",
                            (user_id, temp_data[user_id], user_time))
                con.commit()
                con.close()
            bot.send_message(message.chat.id, "Напоминание принято!")
            del user_state[user_id]
            del temp_data[user_id]
        except ValueError:
            bot.send_message(message.chat.id, '«Неверный формат, попробуйте ещё раз»')

def check_reminders():
    while True:
        try:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")

            with db_lock:
                con = sqlite3.connect('.venv/reminders.db')
                cursor = con.cursor()

                cursor.execute("SELECT id, user_id, text, time FROM reminders WHERE time = ?", (current_time,))
                reminders_list = cursor.fetchall()

                for reminder in reminders_list:
                    reminder_id = reminder[0]
                    cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))

                con.commit()
                con.close()

            for reminder in reminders_list:
                u_id = reminder[1]
                u_text = reminder[2]
                u_time = reminder[3]

                bot.send_message(u_id, f'<b>⏰ Напоминание:</b> \n{u_text} в {u_time}', parse_mode='HTML')
            sleep(50)

        except Exception as e:
            print(f'Ошибка {e}')


thread = threading.Thread(
    target=check_reminders,
    daemon=True)
thread.start()

bot.infinity_polling(
    timeout=20,
    long_polling_timeout=60,
    skip_pending=True
)