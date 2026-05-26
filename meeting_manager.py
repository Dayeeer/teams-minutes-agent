import sqlite3
from datetime import datetime
from pathlib import Path

DATABASE_DIR = Path("data")
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "meetings.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def current_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meetings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,

        workspace_id TEXT NOT NULL,
        created_by TEXT NOT NULL,

        meeting_title TEXT NOT NULL,
        meeting_link TEXT,

        transcript_language TEXT,
        summary_mode TEXT,
        special_instructions TEXT,

        transcript_text TEXT,
        transcript_status TEXT DEFAULT 'manual_only',
        auto_fetch_attempts INTEGER DEFAULT 0,
        last_transcript_check TEXT,

        summary_html TEXT,

        onenote_page_url TEXT,
        onenote_page_id TEXT,

        outlook_draft_id TEXT,
        outlook_draft_subject TEXT,

        status TEXT NOT NULL
    )
    """)

    connection.commit()
    connection.close()


def create_meeting(
    workspace_id: str,
    created_by: str,
    meeting_title: str,
    meeting_link: str | None = None,
    transcript_language: str | None = None,
    summary_mode: str | None = None,
    special_instructions: str | None = None,
    transcript_status: str = "manual_only",
) -> int:
    connection = get_connection()
    cursor = connection.cursor()

    now = current_timestamp()

    cursor.execute(
        """
    INSERT INTO meetings (
        created_at,
        updated_at,

        workspace_id,
        created_by,

        meeting_title,
        meeting_link,

        transcript_language,
        summary_mode,
        special_instructions,

        transcript_status,
        auto_fetch_attempts,
        last_transcript_check,

        status
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            now,
            now,
            workspace_id,
            created_by,
            meeting_title,
            meeting_link,
            transcript_language,
            summary_mode,
            special_instructions,
            transcript_status,
            0,
            None,
            "created",
        ),
    )

    meeting_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return meeting_id


def get_meeting(meeting_id: int) -> dict | None:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
    SELECT *
    FROM meetings
    WHERE id = ?
    """,
        (meeting_id,),
    )

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    return dict(row)


def list_recent_meetings(limit: int = 20) -> list[dict]:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
    SELECT *
    FROM meetings
    ORDER BY id DESC
    LIMIT ?
    """,
        (limit,),
    )

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def update_meeting_status(
    meeting_id: int,
    status: str,
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
    UPDATE meetings
    SET
        status = ?,
        updated_at = ?
    WHERE id = ?
    """,
        (
            status,
            current_timestamp(),
            meeting_id,
        ),
    )

    connection.commit()
    connection.close()


def update_meeting_transcript(
    meeting_id: int,
    transcript_text: str,
    transcript_status: str = "manual_uploaded",
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
    UPDATE meetings
    SET
        transcript_text = ?,
        transcript_status = ?,
        updated_at = ?,
        status = ?
    WHERE id = ?
    """,
        (
            transcript_text,
            transcript_status,
            current_timestamp(),
            "transcript_ready",
            meeting_id,
        ),
    )

    connection.commit()
    connection.close()


def update_transcript_fetch_status(
    meeting_id: int,
    transcript_status: str,
    transcript_text: str | None = None,
):
    connection = get_connection()
    cursor = connection.cursor()

    current_meeting = get_meeting(meeting_id)

    if current_meeting is None:
        return {
            "success": False,
            "error": "Meeting not found.",
        }

    current_attempts = current_meeting.get("auto_fetch_attempts") or 0

    if transcript_text is not None:
        cursor.execute(
            """
        UPDATE meetings
        SET
            transcript_status = ?,
            transcript_text = ?,
            auto_fetch_attempts = ?,
            last_transcript_check = ?,
            updated_at = ?,
            status = ?
        WHERE id = ?
        """,
            (
                transcript_status,
                transcript_text,
                current_attempts + 1,
                current_timestamp(),
                current_timestamp(),
                "transcript_ready",
                meeting_id,
            ),
        )

    else:
        cursor.execute(
            """
        UPDATE meetings
        SET
            transcript_status = ?,
            auto_fetch_attempts = ?,
            last_transcript_check = ?,
            updated_at = ?
        WHERE id = ?
        """,
            (
                transcript_status,
                current_attempts + 1,
                current_timestamp(),
                current_timestamp(),
                meeting_id,
            ),
        )

    connection.commit()
    connection.close()

    return {
        "success": True,
    }


def update_meeting_summary(
    meeting_id: int,
    summary_html: str,
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
    UPDATE meetings
    SET
        summary_html = ?,
        updated_at = ?,
        status = ?
    WHERE id = ?
    """,
        (
            summary_html,
            current_timestamp(),
            "summary_generated",
            meeting_id,
        ),
    )

    connection.commit()
    connection.close()


def update_onenote_result(
    meeting_id: int,
    onenote_page_url: str,
    onenote_page_id: str,
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
    UPDATE meetings
    SET
        onenote_page_url = ?,
        onenote_page_id = ?,
        updated_at = ?,
        status = ?
    WHERE id = ?
    """,
        (
            onenote_page_url,
            onenote_page_id,
            current_timestamp(),
            "onenote_created",
            meeting_id,
        ),
    )

    connection.commit()
    connection.close()


def update_outlook_result(
    meeting_id: int,
    draft_id: str,
    draft_subject: str,
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
    UPDATE meetings
    SET
        outlook_draft_id = ?,
        outlook_draft_subject = ?,
        updated_at = ?,
        status = ?
    WHERE id = ?
    """,
        (
            draft_id,
            draft_subject,
            current_timestamp(),
            "outlook_draft_created",
            meeting_id,
        ),
    )

    connection.commit()
    connection.close()
