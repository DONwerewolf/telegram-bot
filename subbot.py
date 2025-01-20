import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = os.getenv("7894513283:AAEaSNn97y7s69Eg7In1PjDLNlHGduuylfc")  # Токен бота берется из переменных окружения

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Я ваш бот.")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
