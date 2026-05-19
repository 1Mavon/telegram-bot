import telebot
from telebot import types
from flask import Flask
from threading import Thread
import os

TOKEN = '8855631374:AAGmsjmQdgOqKUFeYhztd9N5xBqLrh3aQuA'

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)


@app.route('/')
def home():
    return "Bot is running!"


# START

@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    button1 = types.KeyboardButton("📥 Получить подборку")
    button2 = types.KeyboardButton("📷 Instagram")
    button3 = types.KeyboardButton("💬 Поддержка")

    markup.add(button1)
    markup.add(button2, button3)

    text = (
        "🔥 <b>Подборка трендовых образов</b>\n\n"
        "• готовые стильные луки\n"
        "• ссылки на одежду\n"
        "• актуальные тренды\n"
        "• удобный PDF-файл\n\n"
        "👇 Выбери действие:"
    )

    bot.send_message(
        message.chat.id,
        text,
        parse_mode='HTML',
        reply_markup=markup
    )


# BUTTONS

@bot.message_handler(content_types=['text'])
def handle_text(message):

    if message.text == "📥 Получить подборку":

        file = open("outfits.pdf", "rb")

        bot.send_document(
            message.chat.id,
            file,
            caption="🔥 Твоя подборка готова"
        )

    elif message.text == "📷 Instagram":

        bot.send_message(
            message.chat.id,
            "Instagram: https://instagram.com/polifees"
        )

    elif message.text == "💬 Поддержка":

        bot.send_message(
            message.chat.id,
            "По всем вопросам: @polifees"
        )

    else:

        bot.send_message(
            message.chat.id,
            "Нажми кнопку ниже 👇"
        )


# BOT THREAD

def run_bot():
    bot.infinity_polling()


bot_thread = Thread(target=run_bot)
bot_thread.start()


# FLASK

port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)


port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)