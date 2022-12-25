import os
import argparse

from telethon.events import is_handler

from athena.log import get_logger


parser = argparse.ArgumentParser()
parser.add_argument('--run', action='store_true')
parser.add_argument('--init', action='store_true')


logger = get_logger()


if __name__ == '__main__':
    args = parser.parse_args()
    
    if args.run:
        
        # Start the bot
        from athena import bot
        
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        with bot:
            import athena.app as funcs
            for name, entity in funcs.__dict__.items():
                if not name.startswith("__") and is_handler(entity):
                    print(f"added {name} handler")
                    bot.add_event_handler(entity)
            
            logger.info("Athena started")
            bot.start(bot_token=token)
            bot.run_until_disconnected()
            
    if args.init:
        
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
        from athena import init_db
        init_db()