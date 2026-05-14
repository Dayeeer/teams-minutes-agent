import json
from pathlib import Path
from typing import Any, Dict

OUTPUT_DIR = Path("outputs")


def make_safe_filename(title: str) -> str:
    safe_title = "".join(
        c if c.isalnum() or c in (" ", "-", "_") else "_" for c in title
    )
    return safe_title.replace(" ", "_")


def save_outputs_locally(
    meeting_title: str,
    timestamp: str,
    html_output: str,
    text_output: str,
    json_output: Dict[str, Any],
) -> Dict[str, str]:
    """
    Saves generated meeting minutes locally in HTML, TXT and JSON formats.
    Returns file paths as strings.
    """

    OUTPUT_DIR.mkdir(exist_ok=True)

    safe_title = make_safe_filename(meeting_title)
    base_filename = f"{timestamp}_{safe_title}"

    html_path = OUTPUT_DIR / f"{base_filename}.html"
    txt_path = OUTPUT_DIR / f"{base_filename}.txt"
    json_path = OUTPUT_DIR / f"{base_filename}.json"

    html_path.write_text(html_output, encoding="utf-8")
    txt_path.write_text(text_output, encoding="utf-8")
    json_path.write_text(
        json.dumps(json_output, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return {
        "html": str(html_path),
        "txt": str(txt_path),
        "json": str(json_path),
    }
