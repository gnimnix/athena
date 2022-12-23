import logging


logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO,
                    filename="athena.log",
                    force=True)


def get_logger():
    return logging.getLogger(__name__)