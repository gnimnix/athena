import shelve

from contextlib import contextmanager

from athena import session
from athena.log import get_logger
import athena.config
    

@contextmanager
def get_db() -> shelve.DbfilenameShelf:
    """Returns the currently opened connection to the database, creates a new connection if there is none

    Yields:
        Iterator[shelve.DbfilenameShelf]: Database Connection
    """
    try:
        if session.db is None:
            session.db = shelve.open(athena.config.DATABASE.resolve(), writeback=True)
        yield session.db
    finally:
        if session.db is not None:
            session.db.close()
            session.db = None


def init_db() -> None:
    """Handles initiation of database
    """
    logger = get_logger()
    
    with get_db() as db:
        for table in ['records', 'users', 'applications']:
            if table not in db:
                db[table] = {}
        logger.info("Database initiated")


def user_exists(iid: int) -> bool:
    """Check if user exists in the database (i.e. user has registered)

    Args:
        iid (int): Telegram id of user

    Returns:
        bool: True if user exists else False
    """
    with get_db() as db:
        if iid not in db['users']:
            return False
        else:
            return True


def get_auth_level(iid: int) -> int:
    """Get the authentication level of the user

    Args:
        iid (int): Telegram id of user

    Returns:
        int: Authentication level of user
    """
    if not user_exists(iid):
        return False

    with get_db() as db:
        return db['users'][iid]['level']    
