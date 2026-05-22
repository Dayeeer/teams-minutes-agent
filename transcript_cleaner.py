import re

TIMESTAMP_PATTERN = re.compile(r"^\d{1,2}:\d{2}(:\d{2})?")

VTT_TIMESTAMP_PATTERN = re.compile(r"\d{2}:\d{2}:\d{2}\.\d{3}")

SPEAKER_PATTERN = re.compile(r"^[A-Za-zÀ-ÿ0-9 _.-]{1,50}:")


def normalize_line(line: str) -> str:
    return line.strip()


def remove_empty_lines(lines: list[str]) -> list[str]:
    return [line for line in lines if line.strip()]


def is_timestamp_line(line: str) -> bool:
    line = line.strip()

    if "-->" in line:
        return True

    if VTT_TIMESTAMP_PATTERN.search(line):
        return True

    if TIMESTAMP_PATTERN.match(line):
        return True

    return False


def is_metadata_line(line: str) -> bool:
    normalized = line.strip().lower()

    metadata_exact_lines = [
        "webvtt",
        "transcript",
        "recording",
        "live transcript",
        "meeting started",
        "meeting ended",
    ]

    if normalized in metadata_exact_lines:
        return True

    metadata_startswith = [
        "kind:",
        "language:",
        "note",
    ]

    return any(normalized.startswith(prefix) for prefix in metadata_startswith)


def clean_transcript_lines(
    lines: list[str],
) -> list[str]:
    cleaned = []

    for raw_line in lines:
        line = normalize_line(raw_line)

        if not line:
            continue

        if is_timestamp_line(line):
            continue

        if is_metadata_line(line):
            continue

        cleaned.append(line)

    return cleaned


def merge_multiline_speech(
    lines: list[str],
) -> list[str]:
    merged = []

    current_block = ""

    for line in lines:
        if SPEAKER_PATTERN.match(line):
            if current_block:
                merged.append(current_block.strip())

            current_block = line

        else:
            if current_block:
                current_block += " " + line
            else:
                current_block = line

    if current_block:
        merged.append(current_block.strip())

    return merged


def clean_transcript(
    transcript_text: str,
) -> str:
    if not transcript_text:
        return ""

    lines = transcript_text.splitlines()

    lines = clean_transcript_lines(lines)

    lines = remove_empty_lines(lines)

    lines = merge_multiline_speech(lines)

    cleaned_text = "\n".join(lines)

    cleaned_text = re.sub(
        r"\n{3,}",
        "\n\n",
        cleaned_text,
    )

    cleaned_text = cleaned_text.strip()

    return cleaned_text


def extract_speakers(
    transcript_text: str,
) -> list[str]:
    speakers = set()

    for line in transcript_text.splitlines():
        match = SPEAKER_PATTERN.match(line)

        if not match:
            continue

        speaker = match.group(0).rstrip(":").strip()

        if speaker:
            speakers.add(speaker)

    return sorted(speakers)
