from pprint import pprint

from meeting_manager import (
    initialize_database,
    create_meeting,
    get_meeting,
    list_recent_meetings,
)

initialize_database()

meeting_id = create_meeting(
    workspace_id="nrgeer",
    created_by="office@nrgeer.com",
    meeting_title="AI Agent Architecture Discussion",
    meeting_link="https://teams.microsoft.com/test-link",
    transcript_language="English",
    summary_mode="Executive Summary",
    special_instructions="Focus on action items.",
)

print("\nCREATED MEETING ID:\n")
print(meeting_id)

meeting = get_meeting(meeting_id)

print("\nMEETING:\n")
pprint(meeting)

recent = list_recent_meetings()

print("\nRECENT MEETINGS:\n")
pprint(recent)
