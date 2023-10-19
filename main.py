import asyncio
import logging
import os
import datetime
import sys

from aiogram.exceptions import AiogramError

import settings
from models.video_note_info import VideoNotes

# LOGGING ---------

logger = logging.getLogger(__name__)


def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    print(exc_type, exc_value, exc_traceback)


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

import aiogram

logger.info(f'AIOGRAM VERSION: {aiogram.__version__}')

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ContentType

# -----------------

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


def log(message: str):
    logger.info(message)
    print(message)


def get_message_link(message: Message):

    # Приватный чат с пользователем (не возможно сформировать ссылку)
    if message.chat.type == message.from_user.id == message.chat.id:
        return ''

    # Публичная группа
    if message.chat.username:
        return f'https://t.me/{message.chat.username}/{message.message_id}'

    # Приватная группа
    if (correct_id := abs(message.chat.id)) < 1_000_000_000_000:
        return f'https://t.me/c/{correct_id}/{message.message_id}'

    return f'https://t.me/c/{message.chat.shifted_id}/{message.message_id}'


async def get_admin_ids(chat_id: int) -> list[int]:
    members = await bot.get_chat_administrators(chat_id)
    return [
        member.user.id
        for member in members
    ]


async def handle_new_video_note(message: Message):
    log(f'Saved to database')

    vni = VideoNotes(message.video_note.file_unique_id)
    vni.create()


async def handle_duplicate_video_note(message: Message):
    log(f'Found duplicate video')

    admins = get_admin_ids(message.chat.id)

    for admin in await admins:
        try:
            await bot.forward_message(admin, message.chat.id, message.message_id)
            await bot.send_message(
                admin,
                '⚠ <b>Видео-сообщение отправлено повторно.</b>\n'
                f'<a href="tg://user?id={message.from_user.id}">🙈 ОТПРАВИТЕЛЬ</a>',
                parse_mode='HTML'
            )

            log(f'Sent notification to {admin}')

        except AiogramError:
            log(f'Unable to send notification to {admin}')

    if not admins:
        log(f'No admins found in {message.chat.id}')


async def handle_circle_message(message: types.Message):

    # Обрабатываем только видео-заметки
    if message.content_type != ContentType.VIDEO_NOTE:
        await message.answer('Данный бот не предназначен для личной переписки.')
        return

    if message.chat.type == message.from_user.id == message.chat.id:
        await message.answer('Данный бот не предназначен для личной переписки.')
        return

    video_note_id = message.video_note.file_unique_id

    log(f'Got video note with id: {video_note_id}')

    if VideoNotes.contains(video_note_id):
        await handle_duplicate_video_note(message)
        return

    await handle_new_video_note(message)


if __name__ == '__main__':
    dp.message.register(handle_circle_message)

    VideoNotes.init()
    asyncio.run(dp.start_polling(bot))
