import logging


def get_environ(var: str, err_msg: str):
    import os
    try:
        return os.environ[var]
    except KeyError:
        raise KeyError(f'❌ {err_msg}.\n')


BOT_TOKEN = get_environ('TOKEN', 'No bot token specified')
VIDEO_NOTE_DATABASE_PATH = get_environ('VN_DB_PATH', 'No database path specified')
USER_TO_NOTIFY = get_environ('OWNER', 'No owner specified')

LOGGING_LEVEL = logging.INFO
LOGGING_DIRECTORY = get_environ('LOGGING_DIRECTORY', 'No logging directory specified')
LOGGING_FORMAT = '%(filename)s:%(lineno)d #%(levelname)-8s ' \
                 '[%(asctime)s] - %(name)s - %(message)s'
LOGGING_FILENAME_FORMAT = '%Y_%m_%d_%H_%M_%S_%f.log'
