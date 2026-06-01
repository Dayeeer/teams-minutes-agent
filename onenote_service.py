from datetime import datetime
from zoneinfo import ZoneInfo

from config import CONFIG

from microsoft_graph import (
    create_onenote_page,
)


LOCAL_TIMEZONE = ZoneInfo("Europe/Berlin")


def parse_graph_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    normalized = value.replace("Z", "+00:00")

    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    return dt.astimezone(LOCAL_TIMEZONE)


def format_meeting_datetime(start_time: str | None) -> str:
    dt = parse_graph_datetime(start_time)

    if not dt:
        return datetime.now(LOCAL_TIMEZONE).strftime("%Y-%m-%d %H:%M")

    return dt.strftime("%Y-%m-%d %H:%M")


def build_meeting_page_title(
    meeting_title: str,
    start_time: str | None = None,
) -> str:
    meeting_title = meeting_title.strip()

    meeting_datetime = format_meeting_datetime(start_time)

    return f"{meeting_datetime} | {meeting_title}"


def build_onenote_html(
    meeting_title: str,
    summary_html: str,
    created_by: str,
    transcript_language: str,
    summary_mode: str,
    meeting_link: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
) -> str:
    created_at = datetime.now(LOCAL_TIMEZONE).strftime("%Y-%m-%d %H:%M")

    start_dt = parse_graph_datetime(start_time)
    end_dt = parse_graph_datetime(end_time)

    meeting_time_html = ""

    if start_dt and end_dt:
        meeting_time_html = f"""
        <p>
            <strong>Meeting Time:</strong>
            {start_dt.strftime("%Y-%m-%d %H:%M")} - {end_dt.strftime("%H:%M")}
        </p>
        """

    meeting_link_html = ""

    if meeting_link:
        meeting_link_html = f"""
        <p>
            <strong>Meeting Link:</strong><br>
            <a href="{meeting_link}">
                {meeting_link}
            </a>
        </p>
        """

    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>{meeting_title}</title>
    <meta charset="utf-8">
</head>

<body>

    <h1>{meeting_title}</h1>

    {meeting_time_html}

    <p>
        <strong>Note Created:</strong> {created_at}
    </p>

    <p>
        <strong>Created By:</strong> {created_by}
    </p>

    <p>
        <strong>Language:</strong> {transcript_language}
    </p>

    <p>
        <strong>Summary Mode:</strong> {summary_mode}
    </p>

    {meeting_link_html}

    <hr>

    {summary_html}

</body>
</html>
"""


def create_meeting_onenote_page(
    access_token: str,
    meeting_title: str,
    summary_html: str,
    created_by: str,
    transcript_language: str,
    summary_mode: str,
    meeting_link: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
) -> dict:
    page_title = build_meeting_page_title(
        meeting_title=meeting_title,
        start_time=start_time,
    )

    html_content = build_onenote_html(
        meeting_title=page_title,
        summary_html=summary_html,
        created_by=created_by,
        transcript_language=transcript_language,
        summary_mode=summary_mode,
        meeting_link=meeting_link,
        start_time=start_time,
        end_time=end_time,
    )

    result = create_onenote_page(
        access_token=access_token,
        section_id=CONFIG.workspace.onenote_section_id,
        html_content=html_content,
    )

    if not result["success"]:
        return {
            "success": False,
            "error": result.get("error"),
            "details": result,
        }

    data = result["data"]

    return {
        "success": True,
        "page_id": data.get("id"),
        "page_title": data.get("title"),
        "onenote_url": (data.get("links", {}).get("oneNoteWebUrl", {}).get("href")),
        "raw_result": data,
    }
