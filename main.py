import telebot
import schedule
import threading
import time
import random
import csv
import os
from datetime import datetime
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🔐 Токен и канал
BOT_TOKEN = "7451657734:AAHNlKGH6YT2BRErXZV9Y619z7xD1GOY6Qs"
CHANNEL_ID = "@golosbota"

# 📅 Дата запуска
LAUNCH_DATE = datetime(2025, 5, 11)

bot = telebot.TeleBot(BOT_TOKEN)

# 🌐 Flask-сервер для Render и UptimeRobot
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running!'

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# 🔄 Выбор нужного датасета
def get_dataset_file():
    days_since_start = (datetime.now() - LAUNCH_DATE).days
    return "memes_month2.csv" if days_since_start >= 30 else "memes.csv"

# 📥 Загрузка мемов из файла
def load_memes():
    filename = get_dataset_file()
    memes = []
    try:
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            memes = [row['text'] for row in reader if row['text'].strip()]
    except Exception as e:
        print(f"[!] Ошибка загрузки {filename}: {e}")
    return memes

# 📤 Публикация мема в канал
def post_meme():
    memes = load_memes()
    if memes:
        meme = random.choice(memes)
        bot.send_message(CHANNEL_ID, meme)
        print(f"[✓] Мем отправлен: {meme}")
    else:
        print("[!] Мемов не найдено!")

# 🕒 Расписание постинга
schedule.every().day.at("09:00").do(post_meme)
schedule.every().day.at("17:30").do(post_meme)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# 📩 Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Я публикую мемы каждый день в 09:00 и 17:30 🕒\nХочешь мем прямо сейчас? Напиши /meme"
    )

# 🎲 Команда /meme с кнопкой
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

# 🔁 Обработка кнопки "Ещё мем"
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

# 🚀 Запуск
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    threading.Thread(target=run_scheduler).start()
    bot.polling()
