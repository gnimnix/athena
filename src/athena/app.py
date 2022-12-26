from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from athena.log import get_logger
from athena.db import user_exists, get_auth_level
from athena.config import HELP_FILE


def start(update: Update, context: CallbackContext) -> None:
    """'/start' command callback function.
        This is the entry point for the telegram bot

    Args:
        update (Update): None
        context (CallbackContext): None
    """
    logger = get_logger()
    logger.info("User %s used command '/start'", update.message.from_user.id)
    
    user = update.message.from_user
    keyboard = []
    if not user_exists(user.id):
        update.message.reply_text("You are not an authorised user.")
        keyboard.append(["Register"])
        update.message.reply_text(
            "Please register before you can use this bot",
            reply_markup=ReplyKeyboardMarkup(keyboard=keyboard,
                                             one_time_keyboard=True))
        return
    keyboard = [[
        InlineKeyboardButton("Manage SFT Record", callback_data="manage sft")
    ], [InlineKeyboardButton("Apply Off (Not Implemented)", callback_data="2")],
                [InlineKeyboardButton("Get Parade State (Not Implemented)", callback_data="3")]]

    # Only users with 3 and above access level can approve off request
    if get_auth_level(user.id) >= 3:
        keyboard.append(
            [InlineKeyboardButton("Approve Application (Not Implemented)", callback_data="4")])
    update.message.reply_text("Choose Option: ",
                              reply_markup=InlineKeyboardMarkup(keyboard))
    
    
def user_help(update: Update, context: CallbackContext) -> None:
    """
        '/help' command handler

        Args:
            update (Update): None
            context (CallbackContext): None
    """
    logger = get_logger()
    
    with open(HELP_FILE) as file:
        data = file.read()
    update.message.reply_text(data)
    logger.info("User %s used command '/help'", update.message.from_user.id)
