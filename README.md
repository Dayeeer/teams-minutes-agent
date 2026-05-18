# AI Meeting Minutes Agent MVP

AI Meeting Minutes Agent is a local MVP tool designed to process Microsoft Teams meeting transcripts and turn them into structured meeting minutes, action items, decisions, follow-up topics, and draft emails.

The project is currently built as a local Streamlit application and is prepared for future Microsoft Graph integration with Teams, OneNote, and Outlook.

---

# Current Status

The current version works without Microsoft Graph integration.

At this stage, the user can manually paste or upload a Teams transcript, and the app will:

- clean the transcript
- process it with the OpenAI API
- generate structured meeting minutes
- extract key decisions
- extract action items and owners
- identify follow-up topics
- generate an email draft if needed
- support multiple output languages
- save outputs locally
- allow manual editing of generated minutes and email drafts
- register meetings before the call and process them later

---

# Current Workflow

## Quick Process

1. Paste or upload a transcript
2. Select processing mode
3. Select output language
4. Add optional special instructions
5. Generate meeting minutes
6. Review and edit output
7. Download HTML / TXT / JSON / email draft

## Registered Meeting Workflow

1. Register a meeting before the call
2. Save the meeting link, title, language, mode, and instructions
3. After the meeting, upload or paste the transcript
4. Process the meeting using the saved settings
5. Save outputs locally
6. Track the meeting status in the dashboard

---

# Features

## AI Processing

- Meeting summary
- Key decisions
- Action items
- Owners and deadlines
- Main discussion topics
- Open questions
- Follow-up detection
- Email draft generation
- Risks and uncertainties

## Output Modes

- Standard Minutes
- Action Items Only
- Executive Summary

## Output Languages

- English
- Italian
- German
- Russian

## Transcript Input

- Paste transcript manually
- Upload `.txt` transcript
- Upload `.vtt` Teams/WebVTT transcript
- Use sample transcript for testing

## Export Options

- HTML
- TXT
- JSON
- Email draft as TXT

## Local Storage

Generated outputs are saved locally in the `outputs/` folder.

This folder is ignored by Git because meeting outputs may contain sensitive information.

---

# Project Structure

```text
teams-minutes-agent/
│
├── app.py
├── ai_processor.py
├── templates.py
├── transcript_cleaner.py
├── storage.py
├── meeting_manager.py
├── sample_transcript.txt
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
│
├── outputs/          # Local generated outputs, ignored by Git
├── meetings.db       # Local SQLite database, ignored by Git
└── .venv/            # Local virtual environment, ignored by Git
```

---

# Main Files

## `app.py`

Main Streamlit application.

It manages:

- UI
- password access
- quick transcript processing
- meeting registration
- meeting dashboard
- editable output
- download buttons

## `ai_processor.py`

Handles OpenAI API processing.

It sends the transcript to the model and expects structured JSON output.

## `templates.py`

Converts structured AI output into:

- OneNote-style HTML
- plain text minutes

Also supports localized section labels.

## `transcript_cleaner.py`

Cleans Teams/WebVTT transcripts before AI processing.

It removes:

- timestamps
- WebVTT metadata
- empty lines
- unnecessary formatting

## `storage.py`

Saves generated outputs locally as:

- HTML
- TXT
- JSON

## `meeting_manager.py`

Manages registered meetings using SQLite.

It supports:

- creating meetings
- listing meetings
- updating status
- saving output file paths
- deleting meetings

---

# Setup

## 1. Clone the repository

```bash
git clone <repository-url>
cd teams-minutes-agent
```

## 2. Create a virtual environment

### Windows

```bash
py -3.11 -m venv .venv
.venv\Scripts\activate
```

### Mac / Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Create `.env`

Copy `.env.example` and rename it to `.env`.

Then fill in your real values:

```env
OPENAI_API_KEY=your_real_openai_api_key
OPENAI_MODEL=gpt-5.4-mini
APP_PASSWORD=your_local_app_password
```

Important: `.env` must never be committed to GitHub.

---

# Run the App

```bash
streamlit run app.py
```

Then open the local Streamlit URL in the browser.

Use the password defined in `.env`.

---

# Security Notes

Do not commit:

- `.env`
- API keys
- generated meeting outputs
- local database files
- virtual environment files

The following files/folders are ignored by Git:

```text
.env
.venv/
outputs/
meetings.db
*.db
```

---

# Current Limitations

The current version does not yet connect directly to Microsoft Graph.

This means:

- Teams transcript retrieval is not automatic yet
- OneNote page creation is not automatic yet
- Outlook draft creation is not automatic yet

For now, transcripts must be pasted or uploaded manually.

---

# Planned Microsoft Integration

The next development phase will connect the app to Microsoft Graph.

Planned features:

1. Microsoft login / service account connection
2. Fetch Teams transcripts automatically
3. Create OneNote pages automatically
4. Create Outlook draft emails automatically
5. Process registered meetings automatically after transcript availability

Expected future workflow:

```text
Register meeting before call
↓
Teams transcript is created after meeting
↓
Agent retrieves transcript through Microsoft Graph
↓
Transcript is cleaned
↓
OpenAI processes the transcript
↓
OneNote page is created
↓
Outlook draft is created if needed
```

---

# Recommended MVP Usage Today

Until Microsoft Graph integration is ready:

1. Run the app locally
2. Register a meeting before the call
3. Start Teams transcription manually during the meeting
4. After the meeting, download or copy the transcript
5. Upload/paste it into the registered meeting
6. Generate minutes
7. Edit the output if needed
8. Download or manually paste the result into OneNote/email

---

# Development Roadmap

## Completed

- Local Streamlit app
- OpenAI transcript processing
- Structured JSON output
- Transcript cleaner
- Multilingual output
- HTML/TXT/JSON export
- Local output history
- Meeting registration
- Meeting dashboard
- Editable minutes
- Editable email draft

## Next

- README and project cleanup
- Microsoft Entra App Registration
- Microsoft Graph authentication
- OneNote API integration
- Outlook draft API integration
- Teams transcript retrieval
- Automatic processing of registered meetings

---

# Notes

This project is currently an MVP for internal experimentation and learning.

The architecture is intentionally modular so that Microsoft, OpenAI, storage, and UI components can be improved or replaced later without rewriting the full application.