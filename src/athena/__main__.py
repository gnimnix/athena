import os
import argparse
import logging

from telethon import TelegramClient


parser = argparse.ArgumentParser()
parser.add_argument('run')


logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO,
                    filename="athena.log",
                    force=True)
logger = logging.getLogger(__name__)


async def main():
    me = await bot.get_me()
    print(me.stringify())
    

if __name__ == '__main__':
    args = parser.parse_args()
    if args.run:
        from dotenv import load_dotenv
        load_dotenv()
        
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        api_id = os.getenv("TELEGRAM_API_ID")
        api_hash = os.getenv("TELEGRAM_API_HASH")
        bot = TelegramClient('bot', int(api_id), api_hash).start(bot_token=token)
        with bot:
            logger.info("Athena started")
            bot.loop.run_until_complete(main())
