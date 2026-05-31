from urllib.parse import quote

from microsoft_graph import graph_get, graph_get_raw


def find_online_meeting_by_join_url(
    access_token: str,
    join_url: str,
) -> dict:
    encoded_url = quote(join_url, safe="")

    endpoint = "/me/onlineMeetings" f"?$filter=JoinWebUrl eq '{encoded_url}'"

    return graph_get(
        access_token=access_token,
        endpoint=endpoint,
    )


def extract_first_online_meeting(search_result: dict) -> dict | None:
    if not search_result.get("success"):
        return None

    meetings = search_result.get("data", {}).get("value", [])

    if not meetings:
        return None

    return meetings[0]


def list_meeting_transcripts(
    access_token: str,
    online_meeting_id: str,
) -> dict:
    endpoint = f"/me/onlineMeetings/{online_meeting_id}/transcripts"

    return graph_get(
        access_token=access_token,
        endpoint=endpoint,
    )


def extract_first_transcript(transcripts_result: dict) -> dict | None:
    if not transcripts_result.get("success"):
        return None

    transcripts = transcripts_result.get("data", {}).get("value", [])

    if not transcripts:
        return None

    return transcripts[0]


def download_transcript_content(
    access_token: str,
    online_meeting_id: str,
    transcript_id: str,
) -> dict:
    endpoint = (
        f"/me/onlineMeetings/{online_meeting_id}"
        f"/transcripts/{transcript_id}/content"
    )

    return graph_get_raw(
        access_token=access_token,
        endpoint=endpoint,
        accept="text/vtt",
    )


def try_fetch_transcript_from_teams(
    access_token: str,
    meeting_link: str,
) -> dict:
    if not meeting_link or not meeting_link.strip():
        return {
            "success": False,
            "status": "missing_meeting_link",
            "message": "No Teams meeting link provided.",
        }

    meeting_search_result = find_online_meeting_by_join_url(
        access_token=access_token,
        join_url=meeting_link.strip(),
    )

    if not meeting_search_result.get("success"):
        return {
            "success": False,
            "status": "meeting_search_failed",
            "message": "Failed to search online meeting.",
            "details": meeting_search_result,
        }

    meeting = extract_first_online_meeting(meeting_search_result)

    if not meeting:
        return {
            "success": False,
            "status": "meeting_not_found",
            "message": (
                "No online meeting was found for this Teams link. "
                "This can happen if the meeting belongs to another organizer, "
                "if the link format is not searchable, or if the meeting is not accessible "
                "to the connected Microsoft account."
            ),
            "details": meeting_search_result,
        }

    online_meeting_id = meeting.get("id")

    transcripts_result = list_meeting_transcripts(
        access_token=access_token,
        online_meeting_id=online_meeting_id,
    )

    if not transcripts_result.get("success"):
        return {
            "success": False,
            "status": "transcript_list_failed",
            "message": "Failed to list transcripts for this meeting.",
            "meeting": meeting,
            "details": transcripts_result,
        }

    transcript = extract_first_transcript(transcripts_result)

    if not transcript:
        return {
            "success": False,
            "status": "transcript_not_available",
            "message": (
                "The meeting was found, but no transcript is available yet. "
                "Make sure transcription was enabled during the meeting and that the meeting has ended."
            ),
            "meeting": meeting,
            "details": transcripts_result,
        }

    transcript_id = transcript.get("id")

    content_result = download_transcript_content(
        access_token=access_token,
        online_meeting_id=online_meeting_id,
        transcript_id=transcript_id,
    )

    if not content_result.get("success"):
        return {
            "success": False,
            "status": "transcript_download_failed",
            "message": "Transcript was found, but download failed.",
            "meeting": meeting,
            "transcript": transcript,
            "details": content_result,
        }

    return {
        "success": True,
        "status": "transcript_downloaded",
        "message": "Transcript downloaded successfully.",
        "meeting": meeting,
        "transcript": transcript,
        "content": content_result.get("text", ""),
    }
