import telebot
from flask import Flask
from threading import Thread
import os

TOKEN = '8855631374:AAGmsjmQdgOqKUFeYhztd9N5xBqLrh3aQuA'

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)


@app.route('/')
def home():
    return "Bot is running!"


@bot.message_handler(content_types=['text'])
def handle_text(message):

    if message.text.lower() == "хочу лист":

        file = open("outfits.pdf", "rb")

        bot.send_document(
            message.chat.id,
            file,
            caption="Вот твоя подборка 🔥"
        )

    else:
        bot.send_message(
            message.chat.id,
            'Напиши: "хочу лист"'
        )


def run_bot():
    bot.infinity_polling()


bot_thread = Thread(target=run_bot)
bot_thread.start()


port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)