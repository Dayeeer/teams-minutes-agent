from urllib.parse import quote

from microsoft_graph import graph_get_raw

from app.storage.meetings_v2 import (
    ensure_transcript_text_column,
    list_meetings_with_transcript_found,
    update_transcript_text,
    update_meeting_error,
)


def build_online_meetings_prefix(user_id: str | None = None) -> str:
    if user_id:
        return f"/users/{quote(user_id, safe='')}/onlineMeetings"

    return "/me/onlineMeetings"


def download_transcript_content(
    access_token: str,
    online_meeting_id: str,
    transcript_id: str,
    user_id: str | None = None,
) -> str:
    endpoint = (
        f"{build_online_meetings_prefix(user_id)}"
        f"/{online_meeting_id}"
        f"/transcripts/{transcript_id}/content"
    )

    result = graph_get_raw(
        access_token=access_token,
        endpoint=endpoint,
        accept="text/vtt",
    )

    if not result.get("success"):
        raise RuntimeError(result)

    return result.get("text", "")


def process_transcript_downloads(
    access_token: str,
    limit: int = 10,
    user_id: str | None = None,
) -> dict:
    ensure_transcript_text_column()

    meetings = list_meetings_with_transcript_found(limit=limit)

    processed = 0
    downloaded = 0
    errors = 0

    for meeting in meetings:
        processed += 1

        calendar_event_id = meeting["calendar_event_id"]
        online_meeting_id = meeting.get("online_meeting_id")
        transcript_id = meeting.get("transcript_id")

        if not online_meeting_id or not transcript_id:
            update_meeting_error(
                calendar_event_id=calendar_event_id,
                status="transcript_download_error",
                error_message="Missing online_meeting_id or transcript_id.",
            )
            errors += 1
            continue

        try:
            transcript_text = download_transcript_content(
                access_token=access_token,
                online_meeting_id=online_meeting_id,
                transcript_id=transcript_id,
                user_id=user_id,
            )

            update_transcript_text(
                calendar_event_id=calendar_event_id,
                transcript_text=transcript_text,
                status="transcript_downloaded",
            )

            downloaded += 1

        except Exception as exc:
            update_meeting_error(
                calendar_event_id=calendar_event_id,
                status="transcript_download_error",
                error_message=str(exc),
            )
            errors += 1

    return {
        "success": True,
        "processed": processed,
        "downloaded": downloaded,
        "errors": errors,
    }
