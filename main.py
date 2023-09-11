import logging
import os
import datetime
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ContentType, ChatType, Message

import settings
from models.video_note_info import VideoNoteInfo

# LOGGING ---------

logger = logging.getLogger(__name__)


def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


os.makedirs(settings.LOGGING_DIRECTORY, exist_ok=True)

logging_filename = os.path.join(
    settings.LOGGING_DIRECTORY,
    datetime.datetime.now().strftime(
        settings.LOGGING_FILENAME_FORMAT
    )
)

logging.basicConfig(
    level=settings.LOGGING_LEVEL,
    format=settings.LOGGING_FORMAT,
    filename=logging_filename,
    filemode='a'
)

sys.excepthook = log_uncaught_exceptions

# -----------------

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


def get_message_link(message: Message):
    # Приватный чат с пользователем (не возможно сформировать ссылку)
    if message.chat.type == ChatType.PRIVATE:
        return ''

    # Публичная группа
    if message.chat.username:
        return f'https://t.me/{message.chat.username}/{message.message_id}'

    # Приватная группа
    if (correct_id := abs(message.chat.id)) < 1_000_000_000_000:
        return f'https://t.me/c/{correct_id}/{message.message_id}'

    return f'https://t.me/c/{message.chat.shifted_id}/{message.message_id}'


@dp.message_handler(content_types=ContentType.VIDEO_NOTE)
async def handle_circle_message(message: types.Message):
    video_note_id = message.video_note.file_unique_id

    logging.info(f'Got video note with id: {video_note_id}')

    if VideoNoteInfo.get(video_note_id):
        await bot.send_message(
            settings.USER_TO_NOTIFY,
            f"""
⚠ <b>Видео-сообщение отправлено повторно.</b>
<a href="{get_message_link(message)}">👉 видео</a>
            """,
            parse_mode='HTML'
        )

        return

    vni = VideoNoteInfo(
        message.video_note.file_id,
        message.video_note.file_unique_id,
        message.chat.id,
        message.message_id,
        message.from_user.username
    )
    vni.create()

    await bot.send_message(
        settings.USER_TO_NOTIFY,
        f"""
🆕 <b>Видео-сообщение добавлено.</b>
<a href="{get_message_link(message)}">👉 видео</a>
        """,
        parse_mode='HTML'
    )


if __name__ == '__main__':
    from aiogram import executor

    VideoNoteInfo.init()
    executor.start_polling(dp, skip_updates=True)
