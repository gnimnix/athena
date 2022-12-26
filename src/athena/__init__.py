from dotenv import load_dotenv
# Load environment variables
load_dotenv()

import os


from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

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
    
    
    from athena.sft import (sft_submenu_start,
                            AddSFTConversationHandler as add_sft_conv_handler)
    dispatcher.add_handler(CallbackQueryHandler(sft_submenu_start, pattern="^manage sft$"))
    dispatcher.add_handler(add_sft_conv_handler())

    
    from athena.auth import (RegisterConversationHandler as register_conv_handler,
                             ApproveApplicationConversationHandler as approve_conv_handler)
    dispatcher.add_handler(register_conv_handler())
    dispatcher.add_handler(approve_conv_handler())
    
    
    logger.info("telebot started")

    updater.start_polling()
    updater.idle()
