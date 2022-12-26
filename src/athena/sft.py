from datetime import datetime

import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, MessageHandler, Filters, CallbackQueryHandler

import re

from athena.log import get_logger
from athena.config import UPLOAD_FOLDER
from athena.db import get_db, get_auth_level
from athena.models import ExtConversationHandler


def sft_submenu_start(update: Update, context: CallbackContext):
    """Callback query handler when the user selects manage sft

    Args:
        update (Update): None
        context (CallbackContext): None
    """
    query = update.callback_query
    query.answer()
    keyboard = [[
        InlineKeyboardButton("Add SFT Record", callback_data="add sft record")
    ]]

    if get_auth_level(query.from_user.id) >= 3:
        keyboard.append([
            InlineKeyboardButton("Generate Report (Not Implemented)",
                                 callback_data="generate report")
        ])
    query.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(keyboard))


class AddSFTConversationHandler(ExtConversationHandler):
    """Add SFT Record Conversation Handler

    Args:
        ConversationHandler: None
    """
    SFT_START, SFT_PHOTO, SFT_CONFIRM = range(3)

    def __init__(self):
        super().__init__(entry_points=[
            CallbackQueryHandler(self.sft, pattern='^add sft record$')
        ],
                         states={
                             self.SFT_START: [
                                 MessageHandler(Filters.regex("^[0-9]{6}$"),
                                                self.sft_start),
                             ],
                             self.SFT_PHOTO: [
                                 MessageHandler(Filters.photo, self.sft_photo),
                             ],
                             self.SFT_CONFIRM: [
                                 MessageHandler(
                                     Filters.regex(
                                         re.compile("^y|n|yes|no$",
                                                    re.IGNORECASE)),
                                     self.sft_confirm),
                             ]
                         })

    @staticmethod
    def validate_datetime(s: str) -> datetime:
        """Static method that validates a string representing a datetime

        Args:
            s (str): string representing datetime

        Returns:
            Union[bool, datetime.datetime]: datetime object if string
            is valid else False
        """
        return datetime.strptime(s, "%d%m%y")

    def sft(self, update: Update, context: CallbackContext) -> int:
        """Entry point into conversation

        Args:
            update (telegram.Update): None
            context (telegram.CallbackContext): None

        Returns:
            int: value of the current state
        """
        query = update.callback_query
        query.answer()

        self.reset()
        query.edit_message_text(
            "Please enter date of SFT in the format DDMMYY HHMM\nFor e.g. 140322"
        )
        self.CURR_STATE = self.SFT_START
        return self.CURR_STATE

    def sft_start(self, update: Update, context: CallbackContext) -> int:
        """Handler for user to input SFT date

        Args:
            update (telegram.Update): None
            context (telegram.ext.CallbackContext): None

        Returns:
            int: value of the current state
        """
        text = update.message.text

        try:
            date = self.validate_datetime(text)
        except ValueError:
            return self.unknown()

        update.message.reply_text(f"You entered {text}")
        context.user_data['sft_date'] = date

        update.message.reply_text(
            f"Please upload a photo from your exercise app e.g. Strava, Nike")
        self.CURR_STATE = self.SFT_PHOTO
        return self.CURR_STATE

    def sft_photo(self, update: Update, context: CallbackContext) -> int:
        """Handler for user to upload screenshot of exercise

        Args:
            update (telegram.Update): None
            context (telegram.CallbackContext): None

        Returns:
            int: value of the current state
        """

        user_photo_file = update.message.effective_attachment[-1].get_file()
        extension = user_photo_file.file_path.split(".")[-1]
        msg = update.message.reply_text("Retrieving your image...")
        user_photo = user_photo_file.download(
            os.path.join(UPLOAD_FOLDER,
                         user_photo_file.file_unique_id + '.' + extension))
        msg.edit_text("Successfully retrieved your image")

        context.user_data['sft_photo_filepath'] = user_photo

        update.message.reply_text(
            "Please check that you have entered the correct details")
        update.message.reply_text(
            f"SFT Date: {context.user_data['sft_date'].strftime('%d%m%y')}")
        update.message.reply_photo(
            open(context.user_data['sft_photo_filepath'], 'rb'))
        update.message.reply_text("Please enter Y/N to confirm")

        self.CURR_STATE = self.SFT_CONFIRM
        return self.CURR_STATE

    def sft_confirm(self, update: Update, context: CallbackContext) -> int:
        """Handler for user to confirm submission

        Args:
            update (Update): None
            context (CallbackContext): None

        Returns:
            int: value of the current state
        """
        text = update.message.text

        if text.lower() in ['n', 'no']:
            return self.sft(update, context)

        with get_db() as db:
            db[update.message.from_user.id][
                context.user_data['sft_date'].strftime(
                    '%d%m%y')] = context.user_data['sft_photo_filepath']

        update.message.reply_text("Successfully uploaded record")

        self.reset()
        return self.CURR_STATE
