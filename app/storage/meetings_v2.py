import sqlite3
from pathlib import Path


DB_PATH = Path("data/meetings.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS meetings_v2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            calendar_event_id TEXT UNIQUE,

            subject TEXT,
            organizer_email TEXT,

            start_time TEXT,
            end_time TEXT,

            join_url TEXT,

            status TEXT,

            online_meeting_id TEXT,

            transcript_id TEXT,
            transcript_available INTEGER DEFAULT 0,

            onenote_page_id TEXT,

            last_error TEXT,

            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


def upsert_meeting(meeting: dict):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO meetings_v2 (
            calendar_event_id,
            subject,
            organizer_email,
            start_time,
            end_time,
            join_url,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(calendar_event_id)
        DO UPDATE SET
            subject=excluded.subject,
            organizer_email=excluded.organizer_email,
            start_time=excluded.start_time,
            end_time=excluded.end_time,
            join_url=excluded.join_url,
            status=excluded.status,
            updated_at=CURRENT_TIMESTAMP
        """,
        (
            meeting["calendar_event_id"],
            meeting["subject"],
            meeting["organizer_email"],
            meeting["start_time"],
            meeting["end_time"],
            meeting["join_url"],
            meeting["status"],
        ),
    )

    conn.commit()
    conn.close()


def count_meetings() -> int:
    conn = get_connection()

    result = conn.execute(
        "SELECT COUNT(*) FROM meetings_v2"
    ).fetchone()[0]

    conn.close()

    return result
