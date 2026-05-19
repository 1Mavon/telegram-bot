import telebot
from telebot import types
from flask import Flask
from threading import Thread
from yookassa import Configuration, Payment
import uuid
import os

TOKEN = '8855631374:AAGmsjmQdgOqKUFeYhztd9N5xBqLrh3aQuA'

SHOP_ID = '1360096'
SECRET_KEY = 'live_Iw292x0jqiPw1vYlUrCiRjnwy0yvtae63RKyWodY1ec'

Configuration.account_id = SHOP_ID
Configuration.secret_key = SECRET_KEY

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)


@app.route('/')
def home():
    return "Bot is running!"


@bot.message_handler(commands=['start'])
def start(message):

    markup = types.InlineKeyboardMarkup()

    buy_button = types.InlineKeyboardButton(
        " Купить гайд 💓",
        callback_data="buy_guide"
    )

    support_button = types.InlineKeyboardButton(
        "💬 Поддержка",
        url="https://t.me/polifees"
    )

    markup.add(buy_button)
    markup.add(support_button)

    text = (
        "В этом гайде:\n\n"

        "— капсула на лето 2026\n"
        "— 30 вариантов образов\n"
        "— более 30 позиций одежды с ссылками на разный бюджет\n"
        "— подборка стильной обуви и сумок на разный бюджет\n\n"

        "Приобрести можно за 299₽ 👇🏻"
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    if call.data == "buy_guide":

        payment = Payment.create({
            "amount": {
                "value": "299.00",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/polifees_bot"
            },
            "capture": True,
            "description": "Покупка гайда",
            "metadata": {
                "user_id": call.message.chat.id
            }
        }, uuid.uuid4())

        pay_url = payment.confirmation.confirmation_url

        markup = types.InlineKeyboardMarkup()

        pay_button = types.InlineKeyboardButton(
            "💳 Оплатить 299₽",
            url=pay_url
        )

        check_button = types.InlineKeyboardButton(
            "✅ Я оплатил",
            callback_data=f"check_{payment.id}"
        )

        markup.add(pay_button)
        markup.add(check_button)

        bot.send_message(
            call.message.chat.id,
            "Для получения гайда сначала оплати покупку 👇🏻",
            reply_markup=markup
        )

    elif call.data.startswith("check_"):

        payment_id = call.data.replace("check_", "")

        payment = Payment.find_one(payment_id)

        if payment.status == "succeeded":

            bot.send_message(
                call.message.chat.id,
                " Спасибо за покупку за покупку! 💓\n\n"
                "Твой гайд: (на гугл диске)🫶🏻\n"
                "https://drive.google.com/file/d/1-pLgxJxFVs7emmeSOjtBtS9bxxiLHgLw/view?usp=sharing"
            )

        else:

            bot.send_message(
                call.message.chat.id,
                "Оплата пока не найдена"
            )


def run_bot():
    bot.infinity_polling()


bot_thread = Thread(target=run_bot)
bot_thread.start()


port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)