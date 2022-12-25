from dotenv import load_dotenv
# Load environment variables
load_dotenv()

import os
import asyncio

from telethon.sync import TelegramClient


def create_bot(loop):
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    bot = TelegramClient('bot', int(api_id), api_hash, loop=loop)
    bot.session.db = None
    return bot


loop = asyncio.get_event_loop()
bot = create_bot(loop)


# This can only be imported after bot creation
from athena.db import get_db, init_db
