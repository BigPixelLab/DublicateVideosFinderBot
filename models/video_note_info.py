import sqlite3
from dataclasses import dataclass
from typing import Optional

import settings

connection = sqlite3.connect(settings.VIDEO_NOTE_DATABASE_PATH)
db = connection.cursor()


@dataclass
class VideoNoteInfo:
    file_id: str
    file_unique_id: str
    chat_username: str
    message_id: int
    username: str

    def create(self):
        db.execute(f"""
            INSERT INTO saved_video_notes VALUES (?, ?, ?, ?, ?)
        """, [self.file_id, self.file_unique_id, self.chat_username, self.message_id, self.username])

    @classmethod
    def get(cls, file_unique_id) -> Optional['VideoNoteInfo']:
        db.execute("""
            SELECT * FROM saved_video_notes WHERE file_unique_id = ?
        """, [file_unique_id])
        if result := db.fetchone():
            db.fetchall()
            return cls(*result)
        return None

    @classmethod
    def init(cls):
        db.execute("""
            CREATE TABLE IF NOT EXISTS saved_video_notes (
                file_id,
                file_unique_id,
                chat_username,
                message_id,
                username
            )
        """)
