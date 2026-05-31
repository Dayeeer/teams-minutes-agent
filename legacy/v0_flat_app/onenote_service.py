from datetime import datetime

from config import CONFIG

from microsoft_graph import (
    create_onenote_page,
)


def build_meeting_page_title(
    meeting_title: str,
) -> str:
    meeting_title = meeting_title.strip()

    current_date = datetime.now().strftime("%Y-%m-%d")

    return f"{meeting_title} | {current_date}"


def build_onenote_html(
    meeting_title: str,
    summary_html: str,
    created_by: str,
    transcript_language: str,
    summary_mode: str,
    meeting_link: str | None = None,
) -> str:
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

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

    <p>
        <strong>Created:</strong> {created_at}
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
) -> dict:
    page_title = build_meeting_page_title(
        meeting_title=meeting_title,
    )

    html_content = build_onenote_html(
        meeting_title=page_title,
        summary_html=summary_html,
        created_by=created_by,
        transcript_language=transcript_language,
        summary_mode=summary_mode,
        meeting_link=meeting_link,
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
