from transcript_cleaner import (
    clean_transcript,
    extract_speakers,
)

raw_transcript = """
WEBVTT

00:00:01.000 --> 00:00:03.000
Marco: Today we need to decide how to continue the AI project.

00:00:05.000 --> 00:00:07.000
Dasha: I think we should keep transcript upload manual for now.

00:00:09.000 --> 00:00:12.000
Marco:
Agreed.
We should focus on OneNote and Outlook integration first.

Meeting ended
"""


cleaned = clean_transcript(raw_transcript)

print("\nCLEANED TRANSCRIPT:\n")
print(cleaned)

speakers = extract_speakers(cleaned)

print("\nSPEAKERS:\n")
print(speakers)

