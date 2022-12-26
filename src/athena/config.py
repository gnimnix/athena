import pathlib


## PATH CONFIGS
ROOT_PATH = pathlib.Path(__file__).parent
INSTANCE_FOLDER = ROOT_PATH / 'instance/'
UPLOAD_FOLDER = INSTANCE_FOLDER / 'uploads'
HELP_FILE = ROOT_PATH / 'help.txt'

## DATABASE
DATABASE = INSTANCE_FOLDER / 'app.db'

## DATE FORMATTING
DATE_FORMAT = "%Y-%m-%d_%H:%M:%S.%f"
