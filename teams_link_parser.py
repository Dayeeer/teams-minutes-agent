from urllib.parse import urlparse, parse_qs, unquote
import re

TEAMS_DOMAINS = [
    "teams.microsoft.com",
    "teams.live.com",
]


def normalize_url(url: str) -> str:
    if not url:
        return ""

    return url.strip()


def is_teams_url(url: str) -> bool:
    url = normalize_url(url)

    if not url:
        return False

    parsed = urlparse(url)

    return any(domain in parsed.netloc.lower() for domain in TEAMS_DOMAINS)


def extract_meeting_id_from_path(path: str) -> str | None:
    decoded_path = unquote(path)

    patterns = [
        r"/l/meetup-join/([^/?]+)",
        r"meetup-join/([^/?]+)",
        r"/meet/([^/?]+)",
        r"meet/([^/?]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, decoded_path)

        if match:
            return match.group(1)

    return None


def extract_context_from_query(query_params: dict) -> dict:
    context = {}

    raw_context_values = query_params.get("context")

    if not raw_context_values:
        return context

    raw_context = raw_context_values[0]

    decoded_context = unquote(raw_context)

    context["raw_context"] = decoded_context

    tenant_match = re.search(
        r'"Tid":"([^"]+)"',
        decoded_context,
    )

    object_match = re.search(
        r'"Oid":"([^"]+)"',
        decoded_context,
    )

    message_id_match = re.search(
        r'"MessageId":"([^"]+)"',
        decoded_context,
    )

    if tenant_match:
        context["tenant_id"] = tenant_match.group(1)

    if object_match:
        context["organizer_object_id"] = object_match.group(1)

    if message_id_match:
        context["message_id"] = message_id_match.group(1)

    return context


def parse_teams_meeting_link(url: str) -> dict:
    normalized_url = normalize_url(url)

    if not normalized_url:
        return {
            "success": False,
            "error": "Empty meeting link.",
            "original_url": url,
        }

    if not is_teams_url(normalized_url):
        return {
            "success": False,
            "error": "The link does not look like a Microsoft Teams link.",
            "original_url": url,
        }

    parsed = urlparse(normalized_url)

    query_params = parse_qs(parsed.query)

    meeting_id = extract_meeting_id_from_path(parsed.path)

    context = extract_context_from_query(query_params)

    return {
        "success": True,
        "original_url": url,
        "normalized_url": normalized_url,
        "domain": parsed.netloc,
        "path": parsed.path,
        "meeting_id": meeting_id,
        "tenant_id": context.get("tenant_id"),
        "organizer_object_id": context.get("organizer_object_id"),
        "message_id": context.get("message_id"),
        "raw_context": context.get("raw_context"),
        "query_params": query_params,
    }


def validate_teams_meeting_link(url: str) -> tuple[bool, str]:
    result = parse_teams_meeting_link(url)

    if not result["success"]:
        return False, result["error"]

    if not result.get("meeting_id"):
        return (
            False,
            "Teams link detected, but meeting ID could not be extracted.",
        )

    return True, "Valid Teams meeting link."
