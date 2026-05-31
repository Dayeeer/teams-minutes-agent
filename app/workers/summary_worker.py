import json

from ai_processor import process_meeting_transcript

from app.storage.meetings_v2 import (
    ensure_summary_columns,
    list_meetings_ready_for_summary,
    update_summary_result,
    update_meeting_error,
)


def process_summaries(limit: int = 10) -> dict:
    ensure_summary_columns()

    meetings = list_meetings_ready_for_summary(limit=limit)

    processed = 0
    generated = 0
    errors = 0

    for meeting in meetings:
        processed += 1

        calendar_event_id = meeting["calendar_event_id"]
        subject = meeting.get("subject") or "Untitled Meeting"
        transcript_text = meeting.get("transcript_text") or ""

        try:
            ai_result = process_meeting_transcript(
                transcript=transcript_text,
                meeting_title=subject,
                transcript_language="English",
                summary_mode="Standard Minutes",
                special_instructions=(
                    "Focus on decisions, action items, owners, follow-ups, "
                    "open questions, and topics requiring email follow-up."
                ),
            )

            summary_text = ai_result.get("summary", "")

            update_summary_result(
                calendar_event_id=calendar_event_id,
                summary_text=summary_text,
                summary_json=json.dumps(ai_result, ensure_ascii=False),
            )

            generated += 1

        except Exception as exc:
            update_meeting_error(
                calendar_event_id=calendar_event_id,
                status="summary_error",
                error_message=str(exc),
            )
            errors += 1

    return {
        "success": True,
        "processed": processed,
        "generated": generated,
        "errors": errors,
    }
