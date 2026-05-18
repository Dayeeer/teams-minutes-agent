import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

DB_PATH = "meetings.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_title TEXT NOT NULL,
            meeting_link TEXT,
            mode TEXT NOT NULL,
            output_language TEXT NOT NULL,
            special_instructions TEXT,
            create_email INTEGER DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'registered',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_processed_at TEXT,
            output_html_path TEXT,
            output_txt_path TEXT,
            output_json_path TEXT
        )
        """)

    conn.commit()
    conn.close()


def create_meeting(
    meeting_title: str,
    meeting_link: str,
    mode: str,
    output_language: str,
    special_instructions: str,
    create_email: bool,
) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    timestamp = now_iso()

    cursor.execute(
        """
        INSERT INTO meetings (
            meeting_title,
            meeting_link,
            mode,
            output_language,
            special_instructions,
            create_email,
            status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            meeting_title,
            meeting_link,
            mode,
            output_language,
            special_instructions,
            int(create_email),
            "registered",
            timestamp,
            timestamp,
        ),
    )

    meeting_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return meeting_id


def list_meetings() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM meetings
        ORDER BY created_at DESC
        """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_meeting(meeting_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM meetings
        WHERE id = ?
        """,
        (meeting_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return dict(row)


def update_meeting_status(
    meeting_id: int,
    status: str,
) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE meetings
        SET status = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            status,
            now_iso(),
            meeting_id,
        ),
    )

    conn.commit()
    conn.close()


def update_meeting_outputs(
    meeting_id: int,
    html_path: Optional[str],
    txt_path: Optional[str],
    json_path: Optional[str],
) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    timestamp = now_iso()

    cursor.execute(
        """
        UPDATE meetings
        SET status = ?,
            last_processed_at = ?,
            updated_at = ?,
            output_html_path = ?,
            output_txt_path = ?,
            output_json_path = ?
        WHERE id = ?
        """,
        (
            "completed",
            timestamp,
            timestamp,
            html_path,
            txt_path,
            json_path,
            meeting_id,
        ),
    )

    conn.commit()
    conn.close()


def delete_meeting(meeting_id: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM meetings
        WHERE id = ?
        """,
        (meeting_id,),
    )

    conn.commit()
    conn.close()
