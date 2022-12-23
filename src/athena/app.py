import os

from telethon.sync import TelegramClient, events


api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
bot = TelegramClient('bot', int(api_id), api_hash)


@bot.on(events.NewMessage)
async def echo(event):
    await event.reply(event.raw_text)
