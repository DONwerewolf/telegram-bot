import os
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

# Предоставленные вами API ID и HASH
api_id = '28578552'
api_hash = '84bb1b296c481c316ede93efbb5ba606'

client = TelegramClient('session_name', api_id, api_hash)

def update_media_scanner(file_path):
    cmd = f'am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{file_path}'
    os.system(cmd)
    print(f"Media scanner updated for: {file_path}")  # Отладочное сообщение

@client.on(events.NewMessage(pattern='\\.', outgoing=True))
async def handler(event):
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        if isinstance(reply_msg.media, (MessageMediaPhoto, MessageMediaDocument)):
            try:
                # Загружаем медиа-файл
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

client.start()
client.run_until_disconnected()
