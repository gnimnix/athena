import shelve

from athena import bot
from athena.log import get_logger

import athena.config


logger = get_logger()
    
    
def get_db():
    if bot.session.db is None:
        bot.session.db = shelve.open(athena.config.DATABASE, writeback=True)
    return bot.session.db


def init_db():
    db = get_db()
    for table in ['records', 'users', 'applications']:
        if table not in db:
            db[table] = {}
    logger.info("Database initiated")