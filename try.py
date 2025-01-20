from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import sqlite3
import asyncio

# Ваш токен
API_TOKEN = '8040979371:AAHEkD3ORiA-POeMPUbOSUbGQXCPKagDxDU'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Подключение к базе данных
conn = sqlite3.connect('chat.db')
cursor = conn.cursor()

# Создание таблиц
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    theme TEXT,
                    chat_id INTEGER,
                    is_premium INTEGER DEFAULT 0,
                    stars INTEGER DEFAULT 0)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS complaints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    reported_user_id INTEGER,
                    reason TEXT)''')
conn.commit()

# Очередь для поиска собеседников
queue = {}

# Стоимость премиума в звёздах
PREMIUM_COST = 100  # Например, 100 звёзд за премиум

# Команда /start
@dp.message(Command('start'))
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Общие интересы")],
            [types.KeyboardButton(text="Флирт")],
            [types.KeyboardButton(text="18+")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите тему для общения:", reply_markup=keyboard)

# Обработка выбора темы
@dp.message(lambda message: message.text in ["Общие интересы", "Флирт", "18+"])
async def choose_theme(message: types.Message):
    user_id = message.from_user.id
    theme = message.text

    # Сохраняем выбор пользователя
    cursor.execute('INSERT OR REPLACE INTO users (user_id, theme) VALUES (?, ?)', (user_id, theme))
    conn.commit()

    # Ищем собеседника
    for uid, data in queue.items():
        if data['theme'] == theme and uid != user_id:
            # Нашли собеседника
            chat_id = data['chat_id']
            queue.pop(uid)
            await bot.send_message(chat_id, "Собеседник найден! Начинайте общение.")
            await message.answer("Собеседник найден! Начинайте общение.")
            # Сохраняем ID чата
            cursor.execute('UPDATE users SET chat_id = ? WHERE user_id = ?', (chat_id, user_id))
            cursor.execute('UPDATE users SET chat_id = ? WHERE user_id = ?', (user_id, chat_id))
            conn.commit()
            return

    # Если собеседник не найден, добавляем в очередь
    queue[user_id] = {'theme': theme, 'chat_id': message.chat.id}
    await message.answer("Ищем собеседника...")

# Команда /next
@dp.message(Command('next'))
async def next_chat(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('SELECT chat_id FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result:
        chat_id = result[0]
        # Уведомляем собеседника
        await bot.send_message(chat_id, "Собеседник покинул чат. Ищем нового...")

        # Удаляем данные о чате
        cursor.execute('UPDATE users SET chat_id = NULL WHERE user_id = ?', (user_id,))
        cursor.execute('UPDATE users SET chat_id = NULL WHERE user_id = ?', (chat_id,))
        conn.commit()

        # Ищем нового собеседника
        await choose_theme(message)
    else:
        await message.answer("Ошибка: данные не найдены.")

# Команда /report (пожаловаться на собеседника)
@dp.message(Command('report'))
async def report_user(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('SELECT chat_id FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result:
        chat_id = result[0]
        if chat_id:
            # Сохраняем жалобу
            cursor.execute('INSERT INTO complaints (user_id, reported_user_id, reason) VALUES (?, ?, ?)',
                           (user_id, chat_id, "Нарушение правил"))
            conn.commit()
            await message.answer("Жалоба отправлена. Спасибо за вашу бдительность!")
            await bot.send_message(chat_id, "На вас поступила жалоба. Пожалуйста, соблюдайте правила.")
    else:
        await message.answer("Вы не в чате, чтобы пожаловаться.")

# Команда /premium (премиум-функции)
@dp.message(Command('premium'))
async def premium_features(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('SELECT is_premium FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result:
        is_premium = result[0]
        if is_premium:
            keyboard = types.ReplyKeyboardMarkup(
                keyboard=[
                    [types.KeyboardButton(text="Мужчина")],
                    [types.KeyboardButton(text="Женщина")],
                    [types.KeyboardButton(text="Не важно")]
                ],
                resize_keyboard=True
            )
            await message.answer("Выберите пол собеседника:", reply_markup=keyboard)
        else:
            await message.answer("Эта функция доступна только для премиум-пользователей. Используйте /buy_premium для покупки.")
    else:
        await message.answer("Ошибка: данные не найдены.")

# Команда /buy_premium (покупка премиума за звёзды)
@dp.message(Command('buy_premium'))
async def buy_premium(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('SELECT stars FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result:
        stars = result[0]
        if stars >= PREMIUM_COST:
            # Списание звёзд
            cursor.execute('UPDATE users SET stars = stars - ?, is_premium = 1 WHERE user_id = ?', (PREMIUM_COST, user_id))
            conn.commit()
            await message.answer("Поздравляем! Теперь у вас есть премиум-доступ.")
        else:
            await message.answer(f"Недостаточно звёзд. Вам нужно {PREMIUM_COST - stars} ещё звёзд.")
    else:
        await message.answer("Ошибка: данные не найдены.")

# Команда /add_stars (добавление звёзд через Telegram Stars)
@dp.message(Command('add_stars'))
async def add_stars(message: types.Message):
    user_id = message.from_user.id
    # Создаем инвойс для оплаты звёздами
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Покупка звёзд",
        description="Купите звёзды для премиум-функций.",
        payload="stars_payment",
        provider_token="ВАШ_PROVIDER_TOKEN",  # Замените на ваш токен платежной системы
        currency="USD",
        prices=[types.LabeledPrice(label="100 звёзд", amount=10000)]  # 100 звёзд за $10 (в центах)
    )

# Обработка успешной оплаты
@dp.message(F.content_type == types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    user_id = message.from_user.id
    # Добавляем звёзды пользователю
    cursor.execute('UPDATE users SET stars = stars + 100 WHERE user_id = ?', (user_id,))
    conn.commit()
    await message.answer("Оплата прошла успешно! Вам начислено 100 звёзд.")

# Пересылка сообщений между пользователями
@dp.message()
async def forward_message(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('SELECT chat_id FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result:
        chat_id = result[0]
        if chat_id:
            await bot.send_message(chat_id, message.text)
    else:
        await message.answer("Ошибка: данные не найдены.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
