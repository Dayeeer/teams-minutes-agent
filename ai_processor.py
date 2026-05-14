import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MEETING_MINUTES_SCHEMA = {
    "name": "meeting_minutes",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "meeting_summary": {"type": "array", "items": {"type": "string"}},
            "key_decisions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "decision": {"type": "string"},
                        "confidence": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                        },
                    },
                    "required": ["decision", "confidence"],
                },
            },
            "action_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "owner": {"type": "string"},
                        "task": {"type": "string"},
                        "deadline": {"type": "string"},
                        "confidence": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                        },
                    },
                    "required": ["owner", "task", "deadline", "confidence"],
                },
            },
            "main_topics": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "topic": {"type": "string"},
                        "summary": {"type": "string"},
                    },
                    "required": ["topic", "summary"],
                },
            },
            "open_questions": {"type": "array", "items": {"type": "string"}},
            "follow_up_required": {"type": "boolean"},
            "follow_up_reason": {"type": "string"},
            "email_draft": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "needed": {"type": "boolean"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["needed", "subject", "body"],
            },
            "risks_or_uncertainties": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "meeting_summary",
            "key_decisions",
            "action_items",
            "main_topics",
            "open_questions",
            "follow_up_required",
            "follow_up_reason",
            "email_draft",
            "risks_or_uncertainties",
        ],
    },
    "strict": True,
}


def build_prompt(transcript: str, meeting_title: str, mode: str) -> str:

    return f"""
You are an expert executive assistant creating professional meeting minutes from a Microsoft Teams transcript.

Meeting title:
{meeting_title}

Processing mode:
{mode}

Your task:
Transform the raw transcript into clear, structured, business-ready meeting notes.

Important rules:
- Use only information present in the transcript.
- Do not invent facts, names, owners, deadlines, or decisions.
- Ignore greetings, repetitions, filler language, and small talk.
- Clearly distinguish between:
  - discussion
  - decision
  - action item
- A decision must be clearly agreed or concluded.
- An action item must contain a clear next step.
- If owner is unclear, write "Owner not specified".
- If deadline is unclear, write "No deadline specified".
- Keep language concise, structured, and professional.
- If no follow-up email is needed:
  - set email_draft.needed to false
  - leave subject/body empty.
- Mention unclear points in risks_or_uncertainties.

Mode behavior:
- Standard Minutes:
  balanced professional output.
- Action Items Only:
  prioritize action items and decisions.
- Executive Summary:
  concise high-level business overview.

Transcript:
{transcript}
"""


def process_transcript(
    transcript: str, meeting_title: str, mode: str
) -> Dict[str, Any]:

    if not transcript.strip():
        raise ValueError("Transcript is empty.")

    prompt = build_prompt(transcript=transcript, meeting_title=meeting_title, mode=mode)

    response = client.responses.create(
        model=MODEL,
        input=[
            {
                "role": "system",
                "content": (
                    "You produce accurate meeting minutes " "in strict valid JSON."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": MEETING_MINUTES_SCHEMA["name"],
                "schema": MEETING_MINUTES_SCHEMA["schema"],
                "strict": True,
            }
        },
        store=False,
    )

    output_text = response.output_text

    return json.loads(output_text)
