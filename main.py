import telebot
import schedule
import threading
import time
import random
import csv
import os
from datetime import datetime

# 🔐 Токен и канал
BOT_TOKEN = "7451657734:AAHNlKGH6YT2BRErXZV9Y619z7xD1GOY6Qs"
CHANNEL_ID = "@golosbota"

# 📅 Дата запуска (можешь заменить на фактическую дату)
LAUNCH_DATE = datetime(2025, 5, 11)

bot = telebot.TeleBot(BOT_TOKEN)

# 🔄 Выбор нужного файла по дате
def get_dataset_file():
    days_since_start = (datetime.now() - LAUNCH_DATE).days
    if days_since_start >= 30:
        return "memes_month2.csv"
    else:
        return "memes.csv"

# 📥 Загрузка мемов из CSV
def load_memes():
    filename = get_dataset_file()
    memes = []
    try:
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            memes = [row['text'] for row in reader if row['text'].strip()]
    except Exception as e:
        print(f"[!] Ошибка загрузки из {filename}: {e}")
    return memes

# 📤 Отправка мема
def post_meme():
    memes = load_memes()
    if memes:
        meme = random.choice(memes)
        bot.send_message(CHANNEL_ID, meme)
        print(f"[✓] Мем отправлен: {meme}")
    else:
        print("[!] Мемов не найдено!")

# 🕒 Расписание
schedule.every().day.at("09:00").do(post_meme)
schedule.every().day.at("17:30").do(post_meme)

# ⏱️ Планировщик в фоне
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# 🧪 Проверка бота
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Мемы публикуются каждый день: в 09:00 и в 17:30 📅")

# 🚀 Запуск
if __name__ == "__main__":
    threading.Thread(target=run_scheduler).start()
    bot.polling()
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Команда /meme с кнопкой
@bot.message_handler(commands=['meme'])
def send_random_meme(message):
    memes = load_memes()
    if memes:
        meme = random.choice(memes)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔄 Ещё мем", callback_data="new_meme"))
        bot.send_message(message.chat.id, meme, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Мемов не найдено 😔")

# Обработка нажатия кнопки
@bot.callback_query_handler(func=lambda call: call.data == "new_meme")
def callback_new_meme(call):
    memes = load_memes()
    if memes:
        new_meme = random.choice(memes)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔄 Ещё мем", callback_data="new_meme"))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=new_meme,
            reply_markup=markup
        )
