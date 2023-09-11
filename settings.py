
def get_environ(var: str, err_msg: str):
    import os
    try:
        return os.environ[var]
    except KeyError:
        raise KeyError(f'❌ {err_msg}.\n')


BOT_TOKEN = get_environ('TOKEN', 'No bot token specified')
VIDEO_NOTE_DATABASE_PATH = get_environ('VN_DB_PATH', 'No database path specified')
USER_TO_NOTIFY = get_environ('OWNER', 'No owner specified')
