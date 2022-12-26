import functools

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler, Filters, MessageHandler

from athena.db import get_db
from athena.log import get_logger
from athena.models import ExtConversationHandler


class RegisterConversationHandler(ExtConversationHandler):
    NAME, TEAM_NO = range(2)

    def __init__(self):
        super().__init__(entry_points=[
            MessageHandler(Filters.regex("^Register$"), self.register)
        ],
                         states={
                             self.__class__.NAME:
                             [MessageHandler(Filters.all, self.get_name)],
                             self.__class__.TEAM_NO: [
                                 MessageHandler(
                                     Filters.regex("^[0-9]|1[0-6]$"),
                                     self.get_team_no)
                             ]
                         },
                         fallbacks=[CommandHandler('retry', self.retry)])
        self.CURR_STATE = ConversationHandler.END

    def register(self, update, context):
        logger = get_logger()
        
        user = update.message.from_user
        logger.info("User %s began registering a new account", user.id)

        self.reset()
        update.message.reply_text("Please enter your name")
        update.message.reply_text("Do not enter your rank")
        self.CURR_STATE = self.__class__.NAME
        return self.CURR_STATE

    def retry(self, update, context):
        return self.register(update, context)

    def get_name(self, update, context):
        user_name = update.message.text
        update.message.reply_text(f"You have entered {user_name} as your name")
        update.message.reply_text(
            "If you would like to retry, please enter '/retry'")
        update.message.reply_text(
            "else you can enter your team number (0 for PLHQ)")

        self.state['name'] = user_name
        self.CURR_STATE = self.__class__.TEAM_NO
        return self.CURR_STATE

    def get_team_no(self, update, context):
        logger = get_logger()
        
        team_no = update.message.text

        update.message.reply_text(
            f"You have entered {team_no if team_no != '0' else 'PLHQ'} as your team number"
        )

        user = update.message.from_user
        with get_db() as db:
            if user.id in db['users']:
                update.message.reply_text("You are already a registered user")
            elif user.id in db['applications']:
                update.message.reply_text(
                    "You have already submitted a registration application")
                update.message.reply_text("Please wait for approval")
            else:
                db['applications'][user.id] = {
                    'name': self.state['name'],
                    'team_no': team_no
                }
                update.message.reply_text(
                    "You have successfully submitted an application,\
please wait for one of the administrators to approve your registration.")
                logger.info("User %s successfully submitted application",
                            user.id)

        self.reset()
        return self.CURR_STATE


def auth_required(level):
    """Wrapper to add a check that user has sufficient authentication to execute command

    Args:
        level (int): Integer stating the minimum authentication level required
    """

    def helper(func):

        @functools.wraps(func)
        def check_auth(obj=None, update=None, context=None):
            user = update.message.from_user
            with get_db() as db:
                if user.id in db['users'] and\
                    db['users'][user.id]['level'] >= level:
                    return func(obj, update, context)
                else:
                    update.message.reply_text(
                        "You do not have permission to use this command")
                    return ConversationHandler.END

        return check_auth

    return helper


class ApproveApplicationConversationHandler(ExtConversationHandler):
    AUTH, LEVEL = range(2)

    def __init__(self):
        super().__init__(
            entry_points=[
                MessageHandler(Filters.regex("^Approve Application$"),
                               self.authenticate)
            ],
            states={
                self.__class__.AUTH: [
                    CallbackQueryHandler(self.approve, pattern="^approved"),
                    CallbackQueryHandler(self.reject, pattern="^reject")
                ],
                self.__class__.LEVEL:
                [MessageHandler(Filters.regex("^1|2|3$"), self.level)]
            })

    @auth_required(level=3)
    def authenticate(self, update, context):
        logger = get_logger()
        
        user = update.message.from_user
        logger.info("User %s began approving an application", user.id)

        self.reset()
        with get_db() as db:
            if len(db['applications']) == 0:
                update.message.reply_text("There are no more applications")
                self.reset()
                return ConversationHandler.END
            else:
                update.message.reply_text(
                    f"There are currently {len(db['applications'])} \n\
                    Team 0 is PLHQ.")
                for i, (user_id,
                        info) in enumerate(db['applications'].items()):
                    keyboard = [[
                        InlineKeyboardButton("Approved",
                                             callback_data="approved " +
                                             str(user_id)),
                        InlineKeyboardButton("Reject",
                                             callback_data="reject " +
                                             str(user_id))
                    ]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    update.message.reply_text(
                        f"{i}. {info['name']} registered for team {info['team_no']}",
                        reply_markup=reply_markup)

        self.CURR_STATE = self.AUTH
        return self.CURR_STATE

    def approve(self, update, context):
        query = update.callback_query
        query.answer()
        user_id = int(query.data.split()[1])
        self.state['user_id'] = user_id

        query.edit_message_text(
            text=
            f"Please enter the administrative level of user\n1 - Enlistees\n2 - Team Commanders\n3 - Administrators, Platoon Commanders and PWO"
        )

        self.CURR_STATE = self.LEVEL
        return self.CURR_STATE

    def reject(self, update, context):
        logger = get_logger()
        
        query = update.callback_query
        query.answer()
        user_id = int(query.data.split()[1])

        with get_db() as db:
            if user_id in db['applications']:
                del db['applications'][user_id]

        query.edit_message_text(text=f"Rejected user application")

        user = update.message.from_user
        logger.info("User %s rejected user %s registration application",
                    user.id, user_id)
        return self.authenticate(update, context)

    def level(self, update, context):
        logger = get_logger()
        
        user_id = self.state['user_id']
        level = int(update.message.text)

        with get_db() as db:
            if user_id in db['applications'] and user_id not in db['users']:
                db['users'][user_id] = {
                    'name': db['applications'][user_id]['name'],
                    'team': db['applications'][user_id]['team_no'],
                    'level': level
                }
                del db['applications'][user_id]
            info = db['users'][user_id]

            update.message.reply_text(f"Successfully registered {info['name']}\
                with team {info['team']} with auth level {info['level']}")
            user = update.message.from_user
            logger.info("User %s approved user %s with admin level %s",
                        user.id, user_id, info['level'])
        self.reset()
        return self.CURR_STATE
