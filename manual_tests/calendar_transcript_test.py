from urllib.parse import quote

from auth_service import get_auth_url, authenticate_user
from microsoft_graph import graph_get, graph_get_raw


def get_events(access_token: str) -> list[dict]:
    endpoint = (
        "/me/events"
        "?$top=10"
        "&$orderby=start/dateTime desc"
        "&$select=id,subject,start,end,organizer,isOnlineMeeting,"
        "onlineMeetingProvider,onlineMeetingUrl,onlineMeeting,webLink"
    )

    result = graph_get(access_token=access_token, endpoint=endpoint)

    if not result.get("success"):
        print("\nEVENTS ERROR:")
        print(result)
        raise SystemExit

    return result.get("data", {}).get("value", [])


def get_join_url(event: dict) -> str | None:
    join_url = event.get("onlineMeetingUrl")

    if join_url:
        return join_url

    online_meeting = event.get("onlineMeeting") or {}
    join_url = online_meeting.get("joinUrl")

    if join_url:
        return join_url

    return None


def find_online_meeting_by_join_url(access_token: str, join_url: str) -> dict | None:
    encoded_url = quote(join_url, safe="")
    endpoint = f"/me/onlineMeetings?$filter=JoinWebUrl eq '{encoded_url}'"

    result = graph_get(access_token=access_token, endpoint=endpoint)

    if not result.get("success"):
        print("\nONLINE MEETING SEARCH ERROR:")
        print(result)
        return None

    meetings = result.get("data", {}).get("value", [])

    if not meetings:
        return None

    return meetings[0]


def list_transcripts(access_token: str, online_meeting_id: str) -> list[dict]:
    endpoint = f"/me/onlineMeetings/{online_meeting_id}/transcripts"

    result = graph_get(access_token=access_token, endpoint=endpoint)

    if not result.get("success"):
        print("\nTRANSCRIPTS ERROR:")
        print(result)
        return []

    return result.get("data", {}).get("value", [])


def download_transcript(
    access_token: str,
    online_meeting_id: str,
    transcript_id: str,
) -> str:
    endpoint = (
        f"/me/onlineMeetings/{online_meeting_id}"
        f"/transcripts/{transcript_id}/content"
    )

    result = graph_get_raw(
        access_token=access_token,
        endpoint=endpoint,
        accept="text/vtt",
    )

    if not result.get("success"):
        print("\nTRANSCRIPT DOWNLOAD ERROR:")
        print(result)
        return ""

    return result.get("text", "")


print("\nOPEN THIS URL:\n")
print(get_auth_url())

print("\nAfter login copy only the value after code=\n")

auth_code = input("Paste authorization code:\n").strip()

auth_result = authenticate_user(auth_code)

print("\nAUTH RESULT SUCCESS:")
print(auth_result.get("success"))

if not auth_result.get("success"):
    print(auth_result)
    raise SystemExit

access_token = auth_result["access_token"]

events = get_events(access_token)

online_events = [
    event
    for event in events
    if event.get("isOnlineMeeting")
]

print(f"\nFound {len(events)} calendar events.")
print(f"Found {len(online_events)} online Teams events.\n")

for index, event in enumerate(online_events, start=1):
    subject = event.get("subject", "(no subject)")
    start = event.get("start", {}).get("dateTime", "")
    organizer = (
        event.get("organizer", {})
        .get("emailAddress", {})
        .get("address", "")
    )

    join_url = get_join_url(event)

    print("\n" + "=" * 80)
    print(f"ONLINE EVENT #{index}")
    print("=" * 80)
    print(f"Subject: {subject}")
    print(f"Start: {start}")
    print(f"Organizer: {organizer}")
    print(f"Has onlineMeetingUrl: {bool(event.get('onlineMeetingUrl'))}")
    print(f"Has onlineMeeting object: {bool(event.get('onlineMeeting'))}")
    print(f"Has join URL: {bool(join_url)}")

    if not join_url:
        print("Online meeting lookup: SKIPPED - no join URL available")
        continue

    meeting = find_online_meeting_by_join_url(
        access_token=access_token,
        join_url=join_url,
    )

    if not meeting:
        print("Online meeting lookup: NOT FOUND")
        continue

    online_meeting_id = meeting.get("id")

    print("Online meeting lookup: FOUND")
    print(f"Online meeting ID: {online_meeting_id}")

    transcripts = list_transcripts(
        access_token=access_token,
        online_meeting_id=online_meeting_id,
    )

    print(f"Transcripts found: {len(transcripts)}")

    if not transcripts:
        continue

    transcript = transcripts[0]
    transcript_id = transcript.get("id")

    print(f"First transcript ID: {transcript_id}")
    print(f"Created date/time: {transcript.get('createdDateTime')}")

    content = download_transcript(
        access_token=access_token,
        online_meeting_id=online_meeting_id,
        transcript_id=transcript_id,
    )

    print(f"Transcript content length: {len(content)}")

    if content:
        print("\nTranscript preview:")
        print(content[:500])
        break
