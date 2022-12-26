from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters


class ExtConversationHandler(ConversationHandler):

    def __init__(self,
                 entry_points,
                 states,
                 fallbacks=[],
                 conversation_timeout=600):
        fallbacks.extend([CommandHandler('cancel', self.cancel), MessageHandler(Filters.all, self.unknown)])
        super().__init__(entry_points=entry_points,
                         states=states,
                         fallbacks=fallbacks,
                         conversation_timeout=conversation_timeout)
        self.CURR_STATE = ConversationHandler.END
        self.state = {}

    def reset(self):
        self.CURR_STATE = ConversationHandler.END
        self.state.clear()

    def unknown(self, update, context) -> int:
        """Callback function when the user enters an unrecognisable input

        Args:
            update (Update): None
            context (CallbackContext): None

        Returns:
            int: value of the current state
        """
        update.message.reply_text("Sorry, I didn't understand that message.")
        update.message.reply_text(
            "Please check the format of your input and try again.")
        return self.CURR_STATE

    def cancel(self, update, context) -> int:
        """Callback function when the user cancels the conversation.
            Also invokes the reset function.

        Args:
            update (Update): None
            context (CallbackContext): None

        Returns:
            int: value of the current state
        """
        update.message.reply_text("Cancelled, going back to main menu.")
        self.reset()
        return self.CURR_STATE
