import telebot
from config import TOKEN
from db import init_db
from reminder_checker import start_checker
from handlers import register_handlers

bot = telebot.TeleBot(TOKEN)

init_db()

register_handlers(bot)

start_checker(bot)

bot.infinity_polling(skip_pending=True)
