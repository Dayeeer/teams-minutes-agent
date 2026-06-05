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


def list_meetings_by_status(status: str, limit: int = 20) -> list[dict]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT *
        FROM meetings_v2
        WHERE status = ?
        ORDER BY start_time DESC
        LIMIT ?
        """,
        (status, limit),
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def update_online_meeting_result(
    calendar_event_id: str,
    online_meeting_id: str,
    status: str = "online_meeting_found",
):
    conn = get_connection()

    conn.execute(
        """
        UPDATE meetings_v2
        SET
            online_meeting_id = ?,
            status = ?,
            last_error = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE calendar_event_id = ?
        """,
        (online_meeting_id, status, calendar_event_id),
    )

    conn.commit()
    conn.close()


def update_transcript_result(
    calendar_event_id: str,
    transcript_id: str,
    status: str = "transcript_found",
):
    conn = get_connection()

    conn.execute(
        """
        UPDATE meetings_v2
        SET
            transcript_id = ?,
            transcript_available = 1,
            status = ?,
            last_error = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE calendar_event_id = ?
        """,
        (transcript_id, status, calendar_event_id),
    )

    conn.commit()
    conn.close()


def update_meeting_error(
    calendar_event_id: str,
    status: str,
    error_message: str,
):
    conn = get_connection()

    conn.execute(
        """
        UPDATE meetings_v2
        SET
            status = ?,
            last_error = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE calendar_event_id = ?
        """,
        (status, error_message, calendar_event_id),
    )

    conn.commit()
    conn.close()

def ensure_transcript_text_column():
    conn = get_connection()

    existing_columns = [
        row[1]
        for row in conn.execute("PRAGMA table_info(meetings_v2)").fetchall()
    ]

    if "transcript_text" not in existing_columns:
        conn.execute("ALTER TABLE meetings_v2 ADD COLUMN transcript_text TEXT")

    conn.commit()
    conn.close()


def list_meetings_with_transcript_found(limit: int = 10) -> list[dict]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT *
        FROM meetings_v2
        WHERE status = 'transcript_found'
        AND transcript_id IS NOT NULL
        ORDER BY start_time DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def update_transcript_text(
    calendar_event_id: str,
    transcript_text: str,
    status: str = "transcript_downloaded",
):
    conn = get_connection()

    conn.execute(
        """
        UPDATE meetings_v2
        SET
            transcript_text = ?,
            status = ?,
            last_error = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE calendar_event_id = ?
        """,
        (transcript_text, status, calendar_event_id),
    )

    conn.commit()
    conn.close()

def ensure_summary_columns():
    conn = get_connection()

    existing_columns = [
        row[1]
        for row in conn.execute(
            "PRAGMA table_info(meetings_v2)"
        ).fetchall()
    ]

    if "summary_text" not in existing_columns:
        conn.execute(
            "ALTER TABLE meetings_v2 ADD COLUMN summary_text TEXT"
        )

    if "summary_json" not in existing_columns:
        conn.execute(
            "ALTER TABLE meetings_v2 ADD COLUMN summary_json TEXT"
        )

    conn.commit()
    conn.close()

def list_meetings_ready_for_summary(
    limit: int = 10,
) -> list[dict]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT *
        FROM meetings_v2
        WHERE status = 'transcript_downloaded'
        ORDER BY start_time DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]

def update_summary_result(
    calendar_event_id: str,
    summary_text: str,
    summary_json: str,
):
    conn = get_connection()

    conn.execute(
        """
        UPDATE meetings_v2
        SET
            summary_text = ?,
            summary_json = ?,
            status = 'summary_generated',
            updated_at = CURRENT_TIMESTAMP
        WHERE calendar_event_id = ?
        """,
        (
            summary_text,
            summary_json,
            calendar_event_id,
        ),
    )

    conn.commit()
    conn.close()

def ensure_onenote_columns():
    conn = get_connection()

    existing_columns = [
        row[1]
        for row in conn.execute(
            "PRAGMA table_info(meetings_v2)"
        ).fetchall()
    ]

    if "onenote_page_id" not in existing_columns:
        conn.execute(
            "ALTER TABLE meetings_v2 ADD COLUMN onenote_page_id TEXT"
        )

    if "onenote_url" not in existing_columns:
        conn.execute(
            "ALTER TABLE meetings_v2 ADD COLUMN onenote_url TEXT"
        )

    conn.commit()
    conn.close()


def list_meetings_ready_for_onenote(limit: int = 10) -> list[dict]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT *
        FROM meetings_v2
        WHERE status = 'summary_generated'
        AND (
            onenote_page_id IS NULL
            OR onenote_page_id = ''
        )
        ORDER BY start_time DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]

def update_onenote_result(
    calendar_event_id: str,
    page_id: str,
    page_url: str,
):
    conn = get_connection()

    conn.execute(
        """
        UPDATE meetings_v2
        SET
            onenote_page_id = ?,
            onenote_url = ?,
            status = 'onenote_created',
            last_error = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE calendar_event_id = ?
        """,
        (
            page_id,
            page_url,
            calendar_event_id,
        ),
    )

    conn.commit()
    conn.close()

def ensure_outlook_columns():
    conn = get_connection()

    existing_columns = [
        row[1]
        for row in conn.execute("PRAGMA table_info(meetings_v2)").fetchall()
    ]

    if "outlook_draft_id" not in existing_columns:
        conn.execute("ALTER TABLE meetings_v2 ADD COLUMN outlook_draft_id TEXT")

    if "outlook_draft_subject" not in existing_columns:
        conn.execute("ALTER TABLE meetings_v2 ADD COLUMN outlook_draft_subject TEXT")

    if "outlook_draft_url" not in existing_columns:
        conn.execute("ALTER TABLE meetings_v2 ADD COLUMN outlook_draft_url TEXT")

    conn.commit()
    conn.close()


def list_meetings_ready_for_email_draft(limit: int = 10) -> list[dict]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT *
        FROM meetings_v2
        WHERE status = 'onenote_created'
        AND summary_json IS NOT NULL
        AND (
            outlook_draft_id IS NULL
            OR outlook_draft_id = ''
        )
        ORDER BY start_time DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def update_outlook_draft_result(
    calendar_event_id: str,
    draft_id: str,
    draft_subject: str,
    draft_url: str,
):
    conn = get_connection()

    conn.execute(
        """
        UPDATE meetings_v2
        SET
            outlook_draft_id = ?,
            outlook_draft_subject = ?,
            outlook_draft_url = ?,
            status = 'email_draft_created',
            last_error = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE calendar_event_id = ?
        """,
        (
            draft_id,
            draft_subject,
            draft_url,
            calendar_event_id,
        ),
    )

    conn.commit()
    conn.close()
