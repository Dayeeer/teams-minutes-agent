from pprint import pprint

from storage import (
    save_meeting_artifacts,
)

html_summary = """
<h1>AI Meeting Summary</h1>

<p>
This is a test HTML summary.
</p>
"""

text_summary = """
AI MEETING SUMMARY

This is a test plain text summary.
"""

ai_result = {
    "summary": "Test summary",
    "topics": [
        "Architecture",
        "OneNote",
    ],
    "action_items": [
        "Validate storage layer",
        "Continue app integration",
    ],
}

result = save_meeting_artifacts(
    meeting_title="AI Agent Storage Test",
    html_summary=html_summary,
    text_summary=text_summary,
    ai_result=ai_result,
)

print("\nSTORAGE RESULT:\n")
pprint(result)

