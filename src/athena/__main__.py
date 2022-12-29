import argparse
import threading

from athena.log import get_logger


parser = argparse.ArgumentParser()
parser.add_argument('--run', action='store_true')
parser.add_argument('--init', action='store_true')


if __name__ == '__main__':
    logger = get_logger()
    args = parser.parse_args()
    
    if args.run:
        
        from athena import start_bot
        start_bot()
            
    if args.init:
        
        # Initialize the database
        from athena.db import get_db, init_db
        init_db()
        
        with get_db() as db:
            db['users'][885516278] = {
                'name': 'Lu Xinming',
                'team': '0',
                'level': 3
            }
            
        print("Initiated the database")
