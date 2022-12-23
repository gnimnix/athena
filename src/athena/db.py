import shelve

from athena.log import get_logger


logger = get_logger()


def init_db():
    import athena.config
    with shelve.open(athena.config.DATABASE.as_posix(), writeback=True) as db:
        for table in ['records', 'users', 'applications']:
            if table not in db:
                db[table] = {}
    logger.info("Database initiated")