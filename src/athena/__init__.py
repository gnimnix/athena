from dotenv import load_dotenv
# Load environment variables
load_dotenv()

import os

from threading import Event
from typing import Optional

from telegram.ext import Updater, CommandHandler

from athena.log import get_logger


class Session:
    def __init__(self):
        self.db = None

session = Session()


def start_bot() -> None:
    """Starts the Telegram Bot
    """
    logger = get_logger()
    
    # Create the dirs
    from athena.config import INSTANCE_FOLDER, UPLOAD_FOLDER
    try:
        for folder in [INSTANCE_FOLDER, UPLOAD_FOLDER]:
            os.mkdir(folder.resolve())
    except OSError:
        pass
    
    updater = Updater(token=os.getenv("TELEGRAM_BOT_TOKEN"), use_context=True)
    logger.info(f"Bot #{updater.bot.id} has logged in")
    dispatcher = updater.dispatcher
    
    
    from athena.app import start, user_help
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', user_help))
    
    
    logger.info("telebot started")

    updater.start_polling()
    updater.idle()
