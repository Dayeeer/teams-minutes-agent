from pprint import pprint

from ai_processor import process_meeting_transcript

sample_transcript = """
Marco: Today we need to decide how to continue the AI Meeting Minutes Agent project.
Dasha: I suggest we keep the transcript upload manual for now and focus on OneNote and Outlook integration.
Marco: Agreed. The agent should create pages only in the AI Meeting Minutes notebook under Meeting Summaries.
Dasha: I will clean up the architecture and prepare the production files.
Marco: Good. Please also prepare a short follow-up email draft after the meeting.
"""


result = process_meeting_transcript(
    transcript=sample_transcript,
    meeting_title="AI Agent Architecture Discussion",
    transcript_language="English",
    summary_mode="Executive Summary",
    special_instructions=(
        "Focus on architecture decisions, action items, and follow-up email content."
    ),
)

pprint(result)
