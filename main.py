import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ContentType, ChatType, Message

import settings
from models.video_note_info import VideoNoteInfo

logging.basicConfig(level=logging.INFO)

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
