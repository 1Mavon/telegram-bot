import telebot

TOKEN = '8855631374:AAGmsjmQdgOqKUFeYhztd9N5xBqLrh3aQuA'

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(content_types=['text'])
def handle_text(message):

    if message.text.lower() == "хочу лист":

        file = open("ШОПИНГ-ЛИСТ by polifees🐈‍⬛.pdf", "rb")

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


bot.polling(none_stop=True)