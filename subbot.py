import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Настройки
TOKEN = "7894513283:AAEaSNn97y7s69Eg7In1PjDLNlHGduuylfc"
DB_NAME = "bot.db"

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            channel_id TEXT,
            channel_name TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id INTEGER,
            channel_id TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(channel_id) REFERENCES users(channel_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS queue (
            channel_id TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

# Регистрация канала
def add_channel(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    args = context.args
    if len(args) < 2:
        update.message.reply_text("Используйте команду так: /add @channel_id ChannelName")
        return

    channel_id = args[0]
    channel_name = " ".join(args[1:])

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO users (user_id, channel_id, channel_name) VALUES (?, ?, ?)', 
                   (user_id, channel_id, channel_name))
    conn.commit()
    conn.close()

    update.message.reply_text(f"Канал {channel_name} успешно добавлен!")

# Подписка на каналы
def subscribe(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Получаем один канал для подписки
    cursor.execute('SELECT channel_id, channel_name FROM users WHERE user_id != ? LIMIT 1', (user_id,))
    channel = cursor.fetchone()

    if not channel:
        update.message.reply_text("Пока нет каналов для подписки.")
        return

    channel_id, channel_name = channel

    # Создаем кнопку для подписки
    keyboard = [[InlineKeyboardButton(channel_name, callback_data=f"sub_{channel_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Подпишитесь на этот канал:", reply_markup=reply_markup)

    conn.close()

# Обработка нажатия на кнопку подписки
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    channel_id = query.data.split("_")[1]  # sub_12345 -> 12345

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Добавляем подписку
    cursor.execute('INSERT INTO subscriptions (user_id, channel_id) VALUES (?, ?)', (user_id, channel_id))
    conn.commit()

    # Уведомляем пользователя
    query.answer(f"Вы подписались на канал!")
    query.edit_message_text("Спасибо за подписку! Ожидайте подписчика на ваш канал.")

    # Добавляем канал пользователя в очередь для показа другим
    cursor.execute('SELECT channel_id FROM users WHERE user_id = ?', (user_id,))
    user_channel_id = cursor.fetchone()[0]

    cursor.execute('INSERT INTO queue (channel_id) VALUES (?)', (user_channel_id,))
    conn.commit()

    conn.close()

# Основная функция
def main():
    init_db()

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Команды
    dp.add_handler(CommandHandler("add", add_channel))
    dp.add_handler(CommandHandler("sub", subscribe))

    # Обработка кнопок
    dp.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
