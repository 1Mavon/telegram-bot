import telebot
from telebot import types
from flask import Flask, request
from yookassa import Configuration, Payment
import uuid
import os

# =========================
# НАСТРОЙКИ
# =========================

# Эти значения нужно добавить в Render → Environment Variables
TOKEN = os.environ.get("BOT_TOKEN")
SHOP_ID = os.environ.get("SHOP_ID")
SECRET_KEY = os.environ.get("YOOKASSA_SECRET_KEY")

if not TOKEN or not SHOP_ID or not SECRET_KEY:
    raise RuntimeError(
        "Не заданы BOT_TOKEN, SHOP_ID или YOOKASSA_SECRET_KEY "
        "в переменных окружения Render."
    )

Configuration.account_id = SHOP_ID
Configuration.secret_key = SECRET_KEY

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# PDF должен лежать рядом с bot.py в проекте Render
GUIDE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "SHOPPING LIST FOR AUTUMN'26.pdf"
)

GUIDE_PRICE = "350.00"


# =========================
# ГЛАВНАЯ СТРАНИЦА
# =========================

@app.route("/")
def home():
    return "Bot is running!"


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.InlineKeyboardMarkup()

    buy_button = types.InlineKeyboardButton(
        "Забрать капсулу за 350₽ 🛍",
        callback_data="buy_guide"
    )

    support_button = types.InlineKeyboardButton(
        "💬 Поддержка",
        url="https://t.me/polifees"
    )

    markup.add(buy_button)
    markup.add(support_button)

    text = (
        "SHOPPING LIST FOR AUTUMN’26 🍂\n\n"
        "— стильная осенняя капсула с 35+ готовыми образами "
        "и ссылками на одежду, обувь и сумки под разный бюджет\n\n"
        "— подойдет для учебы, работы в офисе и просто для тех, "
        "кто хочет выглядеть стильно этой осенью\n\n"
        "Забрать капсулу за 350₽ 👇🏻"
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=markup
    )


# =========================
# ОПЛАТА
# =========================

@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    if call.data == "buy_guide":

        payment = Payment.create({
            "amount": {
                "value": GUIDE_PRICE,
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/polifees_bot"
            },
            "capture": True,
            "description": "SHOPPING LIST FOR AUTUMN’26",
            "metadata": {
                "user_id": call.message.chat.id
            }
        }, uuid.uuid4())

        pay_url = payment.confirmation.confirmation_url

        markup = types.InlineKeyboardMarkup()

        pay_button = types.InlineKeyboardButton(
            "💳 Оплатить 350₽",
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
            "Для получения капсулы сначала оплати покупку 👇🏻",
            reply_markup=markup
        )

    elif call.data.startswith("check_"):

        payment_id = call.data.replace("check_", "")

        try:
            payment = Payment.find_one(payment_id)

            if payment.status == "succeeded":

                if not os.path.exists(GUIDE_FILE):
                    bot.send_message(
                        call.message.chat.id,
                        "Оплата прошла успешно, но файл пока недоступен. "
                        "Напиши в поддержку: @polifees"
                    )
                    return

                with open(GUIDE_FILE, "rb") as guide:
                    bot.send_document(
                        call.message.chat.id,
                        guide,
                        caption=(
                            "Спасибо за покупку! 🫶🏻\n\n"
                            "Твоя SHOPPING LIST FOR AUTUMN’26 уже здесь.\n"
                            "Приятного шопинга! 🍂"
                        )
                    )

            else:
                bot.send_message(
                    call.message.chat.id,
                    "Оплата пока не найдена. Если ты уже оплатил(а), "
                    "подожди немного и нажми «Я оплатил» ещё раз."
                )

        except Exception:
            bot.send_message(
                call.message.chat.id,
                "Не удалось проверить оплату. Попробуй ещё раз или "
                "напиши в поддержку: @polifees"
            )


# =========================
# WEBHOOK
# =========================

WEBHOOK_URL = "https://telegram-bot-lqa6.onrender.com"


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200


@app.route("/health")
def health():
    return "OK"


bot.remove_webhook()
bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
