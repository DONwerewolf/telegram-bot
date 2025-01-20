import logging
from telethon import TelegramClient, events
from telethon.tl.types import Channel, Chat

# Уровень логирования
logging.basicConfig(level=logging.DEBUG)

# Ваши значения API ID и API HASH
API_ID = '20496785'
API_HASH = '52220603db0241b2002f002dd79a98fa'

# Новый номер телефона
PHONE_NUMBER = '+79389043272'

client = TelegramClient('user_session', API_ID, API_HASH)

async def check_user_in_groups(user_input):
    user_groups = []
    async for dialog in client.iter_dialogs():
        try:
            if isinstance(dialog.entity, (Channel, Chat)):
                participants = await client.get_participants(dialog)
                for participant in participants:
                    if str(participant.id) == user_input or participant.username == user_input:
                        user_groups.append(dialog.title)
                        break
        except Exception as e:
            logging.error(f"Ошибка при проверке участника в {dialog.title}: {e}")
    return user_groups

async def main():
    await client.start(phone=PHONE_NUMBER)
    me = await client.get_me()
    logging.info(f'Logged in as {me.username}')

    user_input = "input_user_id_or_username"
    user_groups = await check_user_in_groups(user_input)

    if user_groups:
        print(f"Пользователь {user_input} состоит в следующих группах/чатах: {', '.join(user_groups)}")
    else:
        print(f"Не удалось найти пользователя {user_input} в каких-либо группах/чатах.")

with client:
    client.loop.run_until_complete(main())
