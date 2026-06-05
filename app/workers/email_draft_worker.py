import json
from html import escape

from microsoft_graph import create_outlook_draft

from app.storage.meetings_v2 import (
    ensure_outlook_columns,
    list_meetings_ready_for_email_draft,
    update_outlook_draft_result,
    update_meeting_error,
)


def build_list_html(items: list[str]) -> str:
    if not items:
        return "<p>None clearly identified.</p>"

    html = "<ul>"

    for item in items:
        html += f"<li>{escape(str(item))}</li>"

    html += "</ul>"

    return html


def build_email_body_html(meeting: dict, summary_data: dict) -> str:
    recipients = summary_data.get("email_recommended_recipients", [])
    attachments = summary_data.get("email_recommended_attachments", [])
    email_body = summary_data.get("email_body", "")

    onenote_url = meeting.get("onenote_url") or ""

    onenote_html = ""

    if onenote_url:
        onenote_html = f"""
        <p>
            <strong>OneNote meeting note:</strong><br>
            <a href="{escape(onenote_url)}">{escape(onenote_url)}</a>
        </p>
        """

    return f"""
<html>
<body>

<p><strong>Recommended recipient(s):</strong></p>
{build_list_html(recipients)}

<p><strong>Recommended attachment(s):</strong></p>
{build_list_html(attachments)}

<p><em>Please review the recipients, attachments and text before sending.</em></p>

<hr>

<p><strong>Meeting:</strong> {escape(meeting.get("subject") or "")}</p>

{onenote_html}

<hr>

<div>
{escape(email_body).replace(chr(10), "<br>")}
</div>

</body>
</html>
"""


def process_email_drafts(
    access_token: str,
    limit: int = 10,
) -> dict:
    ensure_outlook_columns()

    meetings = list_meetings_ready_for_email_draft(limit=limit)

    processed = 0
    created = 0
    skipped = 0
    errors = 0

    for meeting in meetings:
        processed += 1

        calendar_event_id = meeting["calendar_event_id"]

        try:
            summary_data = json.loads(meeting["summary_json"])

            if not summary_data.get("email_required"):
                skipped += 1
                continue

            subject = summary_data.get("email_subject") or f"Follow-up | {meeting.get('subject')}"

            body_html = build_email_body_html(
                meeting=meeting,
                summary_data=summary_data,
            )

            result = create_outlook_draft(
                access_token=access_token,
                subject=subject,
                body_html=body_html,
                to_recipients=[],
            )

            if not result.get("success"):
                raise RuntimeError(result)

            data = result.get("data", {})

            update_outlook_draft_result(
                calendar_event_id=calendar_event_id,
                draft_id=data.get("id", ""),
                draft_subject=data.get("subject", ""),
                draft_url=data.get("webLink", ""),
            )

            created += 1

        except Exception as exc:
            update_meeting_error(
                calendar_event_id=calendar_event_id,
                status="email_draft_error",
                error_message=str(exc),
            )
            errors += 1

    return {
        "success": True,
        "processed": processed,
        "created": created,
        "skipped": skipped,
        "errors": errors,
    }
