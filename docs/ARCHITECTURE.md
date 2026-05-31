# Teams Minutes Agent Architecture

## Goal

The agent should work as an autonomous Microsoft Teams meeting assistant.

Target flow:

1. office@nrgeer.com is invited to a Teams meeting.
2. The agent detects the meeting from the Office calendar.
3. After the meeting ends, the agent waits for the transcript.
4. The transcript is processed into a structured summary.
5. A OneNote page is created or updated.
6. Topic-specific email drafts are created when needed.
7. Email threads are tracked and relevant updates are fed back into OneNote.

## Main Modules

### app/config

Configuration and environment loading.

### app/graph

Low-level Microsoft Graph client and authentication.

### app/meetings

Calendar events, meeting lifecycle, meeting database records.

### app/transcripts

Teams transcript discovery, download, cleaning and parsing.

### app/summaries

OpenAI processing, summaries, decisions, action items, topic extraction.

### app/onenote

OneNote page creation and updates.

### app/emails

Outlook email drafts, sent messages, thread tracking.

### app/workers

Scheduled background jobs:
- calendar watcher
- meeting tracker
- transcript worker
- email tracker

### app/storage

Database access and file storage helpers.

## Current Legacy Version

The old flat implementation is archived in:

legacy/v0_flat_app/

It should be used as reference only.
