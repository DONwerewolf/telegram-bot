import os
import time
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

# Ваши API ID и HASH, полученные от my.telegram.org
api_id = '28578552'
api_hash = '84bb1b296c481c316ede93efbb5ba606'

client = TelegramClient('bot', api_id, api_hash)

@client.on(events.NewMessage(pattern='/start', outgoing=True))
async def start(event):
    await event.reply('Привет! Это пользователь-бот на Telethon.')

@client.on(events.NewMessage(pattern='/spam', outgoing=True))
async def spam(event):
    args = event.message.raw_text.split()
    if len(args) < 3:
        await event.reply("Использование: /spam количество текст")
        return
    
    try:
        count = int(args[1])  # Получаем количество сообщений
        message_text = ' '.join(args[2:])  # Получаем текст сообщения
        
        for _ in range(count):  # Отправляем каждое сообщение отдельно
            await event.respond(message_text)
    except ValueError:
        await event.reply("Пожалуйста, укажите корректное количество сообщений.")

def update_media_scanner(file_path):
    cmd = f'am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{file_path}'
    os.system(cmd)
    print(f"Media scanner updated for: {file_path}")

@client.on(events.NewMessage(pattern='\\.', outgoing=True))
async def save_media(event):
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        if isinstance(reply_msg.media, (MessageMediaPhoto, MessageMediaDocument)):
            try:
                file_path = await reply_msg.download_media(file='/data/data/com.termux/files/home/storage/shared/')
                print(f"Downloaded media to: {file_path}")
                target_dir = '/storage/emulated/0/DCIM/Telegram/'
                
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                    print(f"Created directory: {target_dir}")

                target_path = os.path.join(target_dir, os.path.basename(file_path))
                os.system(f'mv {file_path} {target_path}')
                print(f"Moved media to: {target_path}")
                
                if os.path.exists(target_path):
                    update_media_scanner(target_path)
                    await event.delete()  # Удаляем команду у обоих пользователей
                else:
                    print("Ошибка: не удалось сохранить медиа.")
            except Exception as e:
                print(f"Ошибка: {e}")
                await event.reply("Error occurred while saving media.")
        else:
            await event.delete()  # Удаляем команду у обоих пользователей в случае ошибки
    else:
        await event.delete()  # Удаляем команду у обоих пользователей в случае неправильного использования

@client.on(events.NewMessage(pattern='/user_info', outgoing=True))
async def user_info(event):
    if event.is_reply:
        replied_msg = await event.get_reply_message()
        user = replied_msg.sender_id
    else:
        user = event.chat_id
    
    sender = await client.get_entity(user)
    user_id = sender.id
    await client.send_message('me', f"ID пользователя: {user_id}")  # Отправка ID в избранные сообщения
    await event.delete()  # Удаляем команду у обоих пользователей

    if event.is_reply:
        await replied_msg.delete()  # Удаляем оригинальное сообщение при reply






import asyncio

@client.on(events.NewMessage(pattern='/expand (.+)', outgoing=True))
async def expand_text(event):
    text = event.pattern_match.group(1)
    await client.delete_messages(event.chat_id, [event.message.id])  # Удаляем исходное сообщение
    
    words = text.split()
    displayed_text = words[0]
    message = await client.send_message(event.chat_id, displayed_text)
    
    for word in words[1:]:
        displayed_text += " " + word
        await client.edit_message(message, displayed_text)
        await asyncio.sleep(0.5)  # Можно регулировать скорость анимации








# Список пользователей в mute-режиме
muted_users = []

@client.on(events.NewMessage(outgoing=True, pattern='/рот_офф'))
async def mute_user(event):
    receiver_id = event.message.to_id.user_id
    if receiver_id not in muted_users:
        muted_users.append(receiver_id)
        await event.respond(f"Пользователь {receiver_id} теперь в mute-режиме.")
    else:
        await event.respond(f"Пользователь {receiver_id} уже в mute-режиме.")

@client.on(events.NewMessage(outgoing=True, pattern='/рот_опен'))
async def unmute_user(event):
    receiver_id = event.message.to_id.user_id
    if receiver_id in muted_users:
        muted_users.remove(receiver_id)
        await event.respond(f"Пользователь {receiver_id} теперь не находится в mute-режиме.")
    else:
        await event.respond(f"Пользователь {receiver_id} уже не находится в mute-режиме.")

@client.on(events.NewMessage(incoming=True))
async def delete_incoming_messages(event):
    if event.sender_id in muted_users:
        await client.delete_messages(event.chat_id, [event.id])
        print(f"Сообщение от пользователя {event.sender_id} в mute-режиме удалено.")


@client.on(events.NewMessage(pattern='/stop_user_bot', outgoing=True))
async def stop_user_bot(event):
    await event.respond("Бот пользователя временно остановлен.")
    exit()  # Останавливает выполнение скрипта бота
















client.start()
client.run_until_disconnected()
