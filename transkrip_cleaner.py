import re


def clean_transcript(raw_text: str) -> str:
    """
    Cleans Microsoft Teams / WebVTT-style transcripts before sending them to AI.
    Keeps speaker names and meaningful text, removes timestamps and metadata.
    """

    if not raw_text:
        return ""

    text = raw_text.replace("\ufeff", "").strip()

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Remove common WebVTT headers / metadata
        if line.upper() in ["WEBVTT", "KIND: captions", "LANGUAGE: en"]:
            continue

        if line.startswith("NOTE"):
            continue

        # Remove timestamp lines like:
        # 00:00:01.000 --> 00:00:05.000
        if re.match(
            r"^\d{2}:\d{2}:\d{2}[.,]\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}[.,]\d{3}",
            line,
        ):
            continue

        # Remove numeric subtitle indexes
        if line.isdigit():
            continue

        # Remove inline timestamp tags like <00:00:01.000>
        line = re.sub(r"<\d{2}:\d{2}:\d{2}[.,]\d{3}>", "", line)

        # Remove basic VTT tags
        line = re.sub(r"</?c[^>]*>", "", line)
        line = re.sub(r"</?v[^>]*>", "", line)

        line = line.strip()

        if line:
            cleaned_lines.append(line)

    # Merge repeated empty spacing
    cleaned_text = "\n".join(cleaned_lines)

    # Reduce excessive whitespace
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
    cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)

    return cleaned_text.strip()


def estimate_transcript_stats(raw_text: str, cleaned_text: str) -> dict:
    raw_chars = len(raw_text or "")
    cleaned_chars = len(cleaned_text or "")

    reduction = 0
    if raw_chars > 0:
        reduction = round((1 - cleaned_chars / raw_chars) * 100, 1)

    return {
        "raw_chars": raw_chars,
        "cleaned_chars": cleaned_chars,
        "reduction_percent": reduction,
    }
