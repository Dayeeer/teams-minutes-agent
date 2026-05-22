from html import escape


def safe_html(text: str) -> str:
    return escape(text.strip())


def build_html_list(items: list[str]) -> str:
    if not items:
        return "<p>No items.</p>"

    html = "<ul>"

    for item in items:
        html += f"<li>{safe_html(item)}</li>"

    html += "</ul>"

    return html


def build_summary_section(summary_text: str) -> str:
    return f"""
    <h2>Executive Summary</h2>

    <p>
        {safe_html(summary_text)}
    </p>
    """


def build_action_items_section(
    action_items: list[str],
) -> str:
    return f"""
    <h2>Action Items</h2>

    {build_html_list(action_items)}
    """


def build_key_topics_section(
    topics: list[str],
) -> str:
    return f"""
    <h2>Key Topics</h2>

    {build_html_list(topics)}
    """


def build_decisions_section(
    decisions: list[str],
) -> str:
    return f"""
    <h2>Decisions</h2>

    {build_html_list(decisions)}
    """


def build_followups_section(
    followups: list[str],
) -> str:
    return f"""
    <h2>Follow-ups</h2>

    {build_html_list(followups)}
    """


def build_transcript_metadata_section(
    created_by: str,
    transcript_language: str,
    summary_mode: str,
) -> str:
    return f"""
    <hr>

    <h2>Metadata</h2>

    <p>
        <strong>Created By:</strong>
        {safe_html(created_by)}
    </p>

    <p>
        <strong>Transcript Language:</strong>
        {safe_html(transcript_language)}
    </p>

    <p>
        <strong>Summary Mode:</strong>
        {safe_html(summary_mode)}
    </p>
    """


def build_full_summary_html(
    summary_text: str,
    action_items: list[str],
    topics: list[str] | None = None,
    decisions: list[str] | None = None,
    followups: list[str] | None = None,
    created_by: str = "",
    transcript_language: str = "",
    summary_mode: str = "",
) -> str:
    html_parts = []

    html_parts.append(build_summary_section(summary_text))

    if topics:
        html_parts.append(build_key_topics_section(topics))

    if decisions:
        html_parts.append(build_decisions_section(decisions))

    html_parts.append(build_action_items_section(action_items))

    if followups:
        html_parts.append(build_followups_section(followups))

    html_parts.append(
        build_transcript_metadata_section(
            created_by=created_by,
            transcript_language=transcript_language,
            summary_mode=summary_mode,
        )
    )

    return "\n".join(html_parts)


def build_plain_text_summary(
    summary_text: str,
    action_items: list[str],
) -> str:
    text = ""

    text += "EXECUTIVE SUMMARY\n"
    text += "=================\n\n"

    text += summary_text.strip()
    text += "\n\n"

    text += "ACTION ITEMS\n"
    text += "============\n\n"

    if not action_items:
        text += "- No action items\n"

    else:
        for item in action_items:
            text += f"- {item.strip()}\n"

    return text
