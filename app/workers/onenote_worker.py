import json

from onenote_service import create_meeting_onenote_page
from templates import build_full_summary_html

from app.storage.meetings_v2 import (
    ensure_onenote_columns,
    list_meetings_ready_for_onenote,
    update_onenote_result,
    update_meeting_error,
)


def process_onenote_pages(
    access_token: str,
    limit: int = 10,
) -> dict:
    ensure_onenote_columns()

    meetings = list_meetings_ready_for_onenote(
        limit=limit,
    )

    processed = 0
    created = 0
    errors = 0

    for meeting in meetings:
        processed += 1

        calendar_event_id = meeting["calendar_event_id"]

        try:
            summary_data = json.loads(
                meeting["summary_json"]
            )

            summary_html = build_full_summary_html(
                summary_text=summary_data.get("summary", ""),
                action_items=summary_data.get("action_items", []),
                topics=summary_data.get("topics", []),
                decisions=summary_data.get("decisions", []),
                followups=summary_data.get("followups", []),
                created_by="AI Teams Agent",
                transcript_language="English",
                summary_mode="Standard Minutes",
            )

            result = create_meeting_onenote_page(
                access_token=access_token,
                meeting_title=meeting["subject"],
                summary_html=summary_html,
                created_by="AI Teams Agent",
                transcript_language="English",
                summary_mode="Standard Minutes",
                meeting_link=meeting.get("join_url"),
                start_time=meeting.get("start_time"),
                end_time=meeting.get("end_time"),
            )

            if not result.get("success"):
                raise RuntimeError(result)

            update_onenote_result(
                calendar_event_id=calendar_event_id,
                page_id=result.get("page_id", ""),
                page_url=result.get("onenote_url", ""),
            )

            created += 1

        except Exception as exc:
            update_meeting_error(
                calendar_event_id=calendar_event_id,
                status="onenote_error",
                error_message=str(exc),
            )

            errors += 1

    return {
        "success": True,
        "processed": processed,
        "created": created,
        "errors": errors,
    }
