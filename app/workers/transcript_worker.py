from urllib.parse import quote

from microsoft_graph import graph_get

from app.storage.meetings_v2 import (
    list_meetings_for_transcript_processing,
    update_online_meeting_result,
    update_transcript_result,
    update_meeting_error,
)


def build_online_meetings_prefix(user_id: str | None = None) -> str:
    if user_id:
        return f"/users/{quote(user_id, safe='')}/onlineMeetings"

    return "/me/onlineMeetings"


def find_online_meeting_by_join_url(
    access_token: str,
    join_url: str,
    user_id: str | None = None,
) -> dict | None:
    encoded_url = quote(join_url, safe="")

    endpoint = (
        f"{build_online_meetings_prefix(user_id)}"
        f"?$filter=JoinWebUrl eq '{encoded_url}'"
    )

    result = graph_get(
        access_token=access_token,
        endpoint=endpoint,
    )

    if not result.get("success"):
        raise RuntimeError(result)

    meetings = result.get("data", {}).get("value", [])

    if not meetings:
        return None

    return meetings[0]


def list_transcripts(
    access_token: str,
    online_meeting_id: str,
    user_id: str | None = None,
) -> list[dict]:
    endpoint = (
        f"{build_online_meetings_prefix(user_id)}"
        f"/{online_meeting_id}/transcripts"
    )

    result = graph_get(
        access_token=access_token,
        endpoint=endpoint,
    )

    if not result.get("success"):
        raise RuntimeError(result)

    return result.get("data", {}).get("value", [])


def process_calendar_detected_meetings(
    access_token: str,
    limit: int = 50,
    user_id: str | None = None,
) -> dict:
    meetings = list_meetings_for_transcript_processing(
        limit=limit,
    )

    processed = 0
    online_found = 0
    transcripts_found = 0
    errors = 0

    for meeting in meetings:
        processed += 1

        calendar_event_id = meeting["calendar_event_id"]
        join_url = meeting.get("join_url")

        if not join_url:
            update_meeting_error(
                calendar_event_id=calendar_event_id,
                status="missing_join_url",
                error_message="Meeting has no join URL.",
            )
            errors += 1
            continue

        try:
            online_meeting = find_online_meeting_by_join_url(
                access_token=access_token,
                join_url=join_url,
                user_id=user_id,
            )

            if not online_meeting:
                update_meeting_error(
                    calendar_event_id=calendar_event_id,
                    status="online_meeting_not_found",
                    error_message="Online meeting not found by join URL.",
                )
                errors += 1
                continue

            online_meeting_id = online_meeting.get("id")

            if not online_meeting_id:
                update_meeting_error(
                    calendar_event_id=calendar_event_id,
                    status="online_meeting_id_missing",
                    error_message="Online meeting found but has no ID.",
                )
                errors += 1
                continue

            update_online_meeting_result(
                calendar_event_id=calendar_event_id,
                online_meeting_id=online_meeting_id,
                status="online_meeting_found",
            )

            online_found += 1

            transcripts = list_transcripts(
                access_token=access_token,
                online_meeting_id=online_meeting_id,
                user_id=user_id,
            )

            if not transcripts:
                update_online_meeting_result(
                    calendar_event_id=calendar_event_id,
                    online_meeting_id=online_meeting_id,
                    status="calendar_detected",
                )
                continue

            transcript = transcripts[0]
            transcript_id = transcript.get("id")

            if not transcript_id:
                update_meeting_error(
                    calendar_event_id=calendar_event_id,
                    status="transcript_id_missing",
                    error_message="Transcript found but has no ID.",
                )
                errors += 1
                continue

            update_transcript_result(
                calendar_event_id=calendar_event_id,
                transcript_id=transcript_id,
                status="transcript_found",
            )

            transcripts_found += 1

        except Exception as exc:
            update_meeting_error(
                calendar_event_id=calendar_event_id,
                status="transcript_worker_error",
                error_message=str(exc),
            )
            errors += 1

    return {
        "success": True,
        "processed": processed,
        "online_found": online_found,
        "transcripts_found": transcripts_found,
        "errors": errors,
    }
