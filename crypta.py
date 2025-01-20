from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import requests
import feedparser

# API для получения курсов криптовалют
CRYPTO_API_URL = "https://api.coingecko.com/api/v3"

# Список криптовалют и их ID в CoinGecko
CRYPTO_IDS = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "bnb": "binancecoin",
    "usdt": "tether",
    "sol": "solana",
    "xrp": "ripple",
    "ada": "cardano",
    "doge": "dogecoin",
    "dot": "polkadot",
    "shib": "shiba-inu",
    "ltc": "litecoin",
    "matic": "matic-network",
    "avax": "avalanche-2",
    "link": "chainlink",
    "atom": "cosmos",
    "uni": "uniswap",
    "trx": "tron",
    "xmr": "monero",
    "etc": "ethereum-classic",
    "xlm": "stellar",
    "algo": "algorand",
    "vet": "vechain",
    "icp": "internet-computer",
    "fil": "filecoin",
    "theta": "theta-token",
    "xtz": "tezos",
    "eos": "eos",
    "neo": "neo",
    "ksm": "kusama",
    "hbar": "hedera-hashgraph",
    "egld": "elrond-erd-2",
    "zec": "zcash",
    "dash": "dash",
    "waves": "waves",
    "enj": "enjincoin",
    "bat": "basic-attention-token",
    "mana": "decentraland",
    "sand": "the-sandbox",
    "gala": "gala",
    "ape": "apecoin",
    "chz": "chiliz",
    "axs": "axie-infinity",
    "comp": "compound-governance-token",
    "yfi": "yearn-finance",
    "mkr": "maker",
    "snx": "havven",
    "crv": "curve-dao-token",
    "1inch": "1inch",
    "uma": "uma",
    "zil": "zilliqa",
    "qtum": "qtum",
    "rvn": "ravencoin",
    "sc": "siacoin",
    "stx": "blockstack",
    "celo": "celo",
    "hbar": "hedera-hashgraph",
    "iost": "iostoken",
    "omg": "omisego",
    "ankr": "ankr",
    "ren": "republic-protocol",
    "skl": "skale",
    "oxt": "orchid-protocol",
    "uma": "uma",
    "bal": "balancer",
    "ogn": "origin-protocol",
    "nkn": "nkn",
    "rsr": "reserve-rights-token",
    "storj": "storj",
    "sushi": "sushi",
    "uma": "uma",
    "band": "band-protocol",
    "lrc": "loopring",
    "cvc": "civic",
    "nmr": "numeraire",
    "rep": "augur",
    "grt": "the-graph",
    "lpt": "livepeer",
    "api3": "api3",
    "rad": "radicle",
    "audio": "audius",
    "rlc": "iexec-rlc",
    "ant": "aragon",
    "farm": "harvest-finance",
    "mir": "mirror-protocol",
    "tlm": "alien-worlds",
    "ilv": "illuvium",
    "slp": "smooth-love-potion",
    "dydx": "dydx",
    "ens": "ethereum-name-service",
    "perp": "perpetual-protocol",
    "rbn": "ribbon-finance",
    "gods": "gods-unchained",
    "imx": "immutable-x",
    "agix": "singularitynet",
    "high": "highstreet",
    "gmt": "stepn",
    "ape": "apecoin",
    "gal": "galxe",
    "woo": "woo-network",
    "jasmy": "jasmycoin",
    "loka": "league-of-kingdoms",
    "pyr": "vulcan-forged",
    "xcn": "chain-2",
    "cvx": "convex-finance",
    "fxs": "frax-share",
    "spell": "spell-token",
    "gmx": "gmx",
    "rdnt": "radiant-capital",
    "stg": "stargate-finance",
    "t": "threshold-network-token",
    "lqty": "liquity",
    "pendle": "pendle",
    "gno": "gnosis",
    "syn": "synapse-2",
    "pla": "playdapp",
    "ach": "alchemy-pay",
    "elon": "dogelon-mars",
    "people": "constitutiondao",
    "time": "chronotech",
    "joe": "joe",
    "alpaca": "alpaca-finance",
    "qi": "qi-dao",
    "mim": "magic-internet-money",
    "ustc": "terraclassicusd",
    "lunc": "terra-luna",
    "floki": "floki-inu",
    "baby": "babydoge-coin",
    "pepe": "pepe",
    "bonk": "bonk"
}

# Портфолио пользователя
user_portfolio = {}

# Главное меню
async def show_main_menu(update: Update):
    keyboard = [
        ["📊 Портфолио", "➕ Добавить крипту"],
        ["📰 Новости", "ℹ️ Помощь"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Главное меню. Выберите действие:",
        reply_markup=reply_markup
    )

# Функция для команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update)

# Функция для команды "📊 Портфолио"
async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_portfolio or not user_portfolio[user_id]:
        await update.message.reply_text("Ваше портфолио пусто. Добавьте криптовалюты с помощью кнопки '➕ Добавить крипту'.")
        return

    # Получаем текущие курсы криптовалют
    response = requests.get(f"{CRYPTO_API_URL}/simple/price", params={"ids": ",".join(CRYPTO_IDS.values()), "vs_currencies": "usd"})
    if response.status_code != 200:
        await update.message.reply_text("Ошибка: не удалось получить курсы криптовалют.")
        return

    prices = response.json()
    total_value = 0
    total_profit = 0
    message = "📊 Ваше портфолио:\n\n"

    for crypto, amount in user_portfolio[user_id].items():
        if crypto in CRYPTO_IDS and CRYPTO_IDS[crypto] in prices:
            current_price = prices[CRYPTO_IDS[crypto]]["usd"]
            current_value = current_price * amount
            total_value += current_value
            total_profit += current_value - (user_portfolio[user_id][crypto] * amount)
            message += f"🔹 {crypto.upper()}: {amount} шт. (${current_value:.2f})\n"

    message += f"\n💵 Общая стоимость: ${total_value:.2f}\n"
    message += f"📈 Прибыль/убыток: ${total_profit:.2f}\n"
    await update.message.reply_text(message)

# Функция для команды "➕ Добавить крипту"
async def add_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("BTC", callback_data="add_btc"),
         InlineKeyboardButton("ETH", callback_data="add_eth"),
         InlineKeyboardButton("BNB", callback_data="add_bnb")],
        [InlineKeyboardButton("SOL", callback_data="add_sol"),
         InlineKeyboardButton("XRP", callback_data="add_xrp"),
         InlineKeyboardButton("ADA", callback_data="add_ada")],
        [InlineKeyboardButton("DOGE", callback_data="add_doge"),
         InlineKeyboardButton("DOT", callback_data="add_dot"),
         InlineKeyboardButton("SHIB", callback_data="add_shib")],
        [InlineKeyboardButton("Назад", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите криптовалюту для добавления в портфолио:", reply_markup=reply_markup)

# Функция для команды "📰 Новости"
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://cryptopanic.com/news/rss/"
    feed = feedparser.parse(url)
    message = "📰 Последние новости:\n\n"
    for entry in feed.entries[:5]:  # Показываем 5 последних новостей
        message += f"🔹 {entry.title}\nСсылка: {entry.link}\n\n"
    await update.message.reply_text(message)

# Функция для команды "ℹ️ Помощь"
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Список команд:\n"
        "📊 Портфолио - Просмотр вашего портфолио\n"
        "➕ Добавить крипту - Добавить криптовалюту в портфолио\n"
        "📰 Новости - Последние новости из мира криптовалют\n"
        "ℹ️ Помощь - Показать список команд"
    )

# Обработчик нажатия на кнопку инлайн-клавиатуры
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "back_to_main":
        # Возврат в главное меню
        await show_main_menu(query)
        return

    if data.startswith("add_"):
        # Обработка добавления криптовалюты
        crypto = data.split("_")[1]
        user_id = query.from_user.id
        if user_id not in user_portfolio:
            user_portfolio[user_id] = {}
        user_portfolio[user_id][crypto] = 1  # Добавляем 1 единицу криптовалюты
        await query.edit_message_text(f"✅ {crypto.upper()} добавлен в ваше портфолио.")

# Основная функция
def main():
    # Создаем приложение с токеном вашего бота
    application = Application.builder().token("7894513283:AAEaSNn97y7s69Eg7In1PjDLNlHGduuylfc").build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Text(["📊 Портфолио"]), portfolio))
    application.add_handler(MessageHandler(filters.Text(["➕ Добавить крипту"]), add_crypto))
    application.add_handler(MessageHandler(filters.Text(["📰 Новости"]), news))
    application.add_handler(MessageHandler(filters.Text(["ℹ️ Помощь"]), help_command))

    # Регистрируем обработчик нажатия на кнопку инлайн-клавиатуры
    application.add_handler(CallbackQueryHandler(button_callback))

    # Запускаем бота
    application.run_polling()

# Запуск
if __name__ == '__main__':
    main()
