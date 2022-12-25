import os
import asyncio
import pytest

from athena import create_bot

import athena.config


@pytest.fixture(autouse=True)
def configure_db(tmpdir):
    athena.config.DATABASE = tmpdir / 'test.db'


def pytest_sessionstart(session):
    loop = asyncio.get_event_loop()
    session.bot = create_bot(loop)
    session.bot.start(os.getenv("TELEGRAM_BOT_TOKEN"))
    
def pytest_sessionfinish(session):
    session.bot.disconnect()
