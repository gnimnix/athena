import pytest
import os

import athena.config

from athena import bot



@pytest.fixture(autouse=True)
def configure_db(tmpdir):
    athena.config.DATABASE = tmpdir / 'test.db'
    

@pytest.fixture(autouse=True)
def start_bot():
    bot.start(bot_token=os.getenv("TELEGRAM_BOT_TOKEN"))
    bot.run_until_disconnected()
    yield
    bot.disconnect()
