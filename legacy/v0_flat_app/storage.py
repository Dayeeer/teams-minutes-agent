import json
from datetime import datetime
from pathlib import Path

BASE_STORAGE_DIR = Path("storage")

HTML_DIR = BASE_STORAGE_DIR / "html"
TEXT_DIR = BASE_STORAGE_DIR / "text"
JSON_DIR = BASE_STORAGE_DIR / "json"

for directory in [
    BASE_STORAGE_DIR,
    HTML_DIR,
    TEXT_DIR,
    JSON_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)


def sanitize_filename(name: str) -> str:
    invalid_characters = [
        "\\",
        "/",
        ":",
        "*",
        "?",
        '"',
        "<",
        ">",
        "|",
    ]

    sanitized = name.strip()

    for char in invalid_characters:
        sanitized = sanitized.replace(char, "_")

    sanitized = sanitized.replace(" ", "_")

    return sanitized


def build_storage_filename(
    meeting_title: str,
    extension: str,
) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    safe_title = sanitize_filename(meeting_title)

    return f"{timestamp}_{safe_title}.{extension}"


def save_html_summary(
    meeting_title: str,
    html_content: str,
) -> str:
    filename = build_storage_filename(
        meeting_title,
        "html",
    )

    path = HTML_DIR / filename

    path.write_text(
        html_content,
        encoding="utf-8",
    )

    return str(path)


def save_text_summary(
    meeting_title: str,
    text_content: str,
) -> str:
    filename = build_storage_filename(
        meeting_title,
        "txt",
    )

    path = TEXT_DIR / filename

    path.write_text(
        text_content,
        encoding="utf-8",
    )

    return str(path)


def save_json_result(
    meeting_title: str,
    data: dict,
) -> str:
    filename = build_storage_filename(
        meeting_title,
        "json",
    )

    path = JSON_DIR / filename

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return str(path)


def save_meeting_artifacts(
    meeting_title: str,
    html_summary: str,
    text_summary: str,
    ai_result: dict,
) -> dict:
    html_path = save_html_summary(
        meeting_title=meeting_title,
        html_content=html_summary,
    )

    text_path = save_text_summary(
        meeting_title=meeting_title,
        text_content=text_summary,
    )

    json_path = save_json_result(
        meeting_title=meeting_title,
        data=ai_result,
    )

    return {
        "html_path": html_path,
        "text_path": text_path,
        "json_path": json_path,
    }


def load_json_file(
    file_path: str,
) -> dict:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    return json.loads(path.read_text(encoding="utf-8"))
