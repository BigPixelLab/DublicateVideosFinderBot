import sqlite3
from dataclasses import dataclass

import settings

connection = sqlite3.connect(settings.VIDEO_NOTE_DATABASE_PATH)


@dataclass
class VideoNotes:
    file_unique_id: str

    def create(self):
        db = connection.cursor()
        db.execute(f"""
            INSERT INTO saved_video_notes VALUES (?)
        """, [self.file_unique_id])
        db.close()

    @classmethod
    def contains(cls, file_unique_id) -> bool:
        db = connection.cursor()
        db.execute("""
            SELECT count(*) FROM saved_video_notes WHERE file_unique_id = ?
        """, [file_unique_id])
        count = int(db.fetchone()[0]) > 0
        db.close()
        return count

    @classmethod
    def init(cls):
        db = connection.cursor()
        db.execute("""
            CREATE TABLE IF NOT EXISTS saved_video_notes (file_unique_id)
        """)
        db.close()
