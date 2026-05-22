import json
from typing import Any

from openai import OpenAI

from config import CONFIG

client = OpenAI(api_key=CONFIG.openai.api_key)


MEETING_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "summary": {
            "type": "string",
            "description": "Concise professional meeting summary.",
        },
        "topics": {
            "type": "array",
            "description": "Main discussion topics.",
            "items": {
                "type": "string",
            },
        },
        "decisions": {
            "type": "array",
            "description": "Clear decisions made during the meeting.",
            "items": {
                "type": "string",
            },
        },
        "action_items": {
            "type": "array",
            "description": "Concrete action items or next steps.",
            "items": {
                "type": "string",
            },
        },
        "followups": {
            "type": "array",
            "description": "Topics or actions requiring follow-up.",
            "items": {
                "type": "string",
            },
        },
        "risks_or_open_questions": {
            "type": "array",
            "description": "Risks, uncertainties, or open questions.",
            "items": {
                "type": "string",
            },
        },
        "email_required": {
            "type": "boolean",
            "description": "Whether a follow-up email draft is useful.",
        },
        "email_subject": {
            "type": "string",
            "description": "Suggested email subject if email_required is true.",
        },
        "email_body": {
            "type": "string",
            "description": "Suggested plain-text email body if email_required is true.",
        },
    },
    "required": [
        "summary",
        "topics",
        "decisions",
        "action_items",
        "followups",
        "risks_or_open_questions",
        "email_required",
        "email_subject",
        "email_body",
    ],
}


def build_system_prompt() -> str:
    return """
You are an expert executive assistant specialized in turning meeting transcripts
into accurate, structured, business-ready meeting minutes.

You must follow these rules:
- Use only information found in the transcript.
- Do not invent facts, decisions, deadlines, owners, or participants.
- If something is unclear, mention it under risks_or_open_questions.
- Extract action items only when a concrete task or next step is present.
- Extract decisions only when a conclusion or agreement is clearly stated.
- Keep the output concise, professional, and useful.
- If no email is needed, set email_required to false and leave email_subject and email_body empty.
- Always return valid JSON according to the provided schema.
"""


def build_user_prompt(
    transcript: str,
    meeting_title: str,
    transcript_language: str,
    summary_mode: str,
    special_instructions: str,
) -> str:
    return f"""
Meeting title:
{meeting_title}

Transcript language / desired output language:
{transcript_language}

Summary mode:
{summary_mode}

Special instructions:
{special_instructions or "None"}

Transcript:
{transcript}
"""


def process_meeting_transcript(
    transcript: str,
    meeting_title: str,
    transcript_language: str,
    summary_mode: str,
    special_instructions: str = "",
) -> dict[str, Any]:
    if not transcript or not transcript.strip():
        raise ValueError("Transcript is empty.")

    response = client.responses.create(
        model=CONFIG.openai.model,
        input=[
            {
                "role": "system",
                "content": build_system_prompt(),
            },
            {
                "role": "user",
                "content": build_user_prompt(
                    transcript=transcript,
                    meeting_title=meeting_title,
                    transcript_language=transcript_language,
                    summary_mode=summary_mode,
                    special_instructions=special_instructions,
                ),
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "meeting_minutes_output",
                "schema": MEETING_OUTPUT_SCHEMA,
                "strict": True,
            }
        },
    )

    raw_output = response.output_text

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Failed to parse AI response as JSON: {error}\n\nRaw output:\n{raw_output}"
        )
