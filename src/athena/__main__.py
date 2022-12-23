import os
import argparse
import logging


from athena.log import get_logger


parser = argparse.ArgumentParser()
parser.add_argument('run')


logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO,
                    filename="athena.log",
                    force=True)
logger = get_logger()
    

if __name__ == '__main__':
    args = parser.parse_args()
    if args.run:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Create the dirs
        from athena.config import INSTANCE_FOLDER, UPLOAD_FOLDER
        try:
            for folder in [INSTANCE_FOLDER, UPLOAD_FOLDER]:
                os.mkdir(folder)
        except OSError:
            pass
        
        # Initialize the database
        import athena.config
        athena.config.DATABASE = athena.config.INSTANCE_FOLDER / 'app.db'
        from athena.db import init_db
        init_db()
        
        # Start the bot
        from athena.app import bot
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        with bot:
            logger.info("Athena started")
            bot.start(bot_token=token)
            bot.run_until_disconnected()
