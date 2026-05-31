from pprint import pprint

from auth_service import (
    get_auth_url,
    authenticate_user,
)

from teams_transcript_service import (
    find_online_meeting_by_join_url,
    extract_online_meeting_from_result,
    list_meeting_transcripts,
    download_transcript_content,
)

print("\nOPEN THIS URL:\n")
print(get_auth_url())

auth_code = input("\nPaste authorization code:\n").strip()

auth_result = authenticate_user(auth_code)

print("\nAUTH RESULT:")
pprint(auth_result)

if not auth_result.get("success"):
    raise SystemExit

access_token = auth_result["access_token"]

join_url = input("\nPaste Teams meeting link:\n").strip()

print("\nFinding online meeting...\n")

meeting_result = find_online_meeting_by_join_url(
    access_token=access_token,
    join_url=join_url,
)

print("\nMEETING SEARCH RESULT:")
pprint(meeting_result)

meeting = extract_online_meeting_from_result(meeting_result)

if not meeting:
    print("\nNo online meeting found for this link.")
    raise SystemExit

online_meeting_id = meeting["id"]

print("\nONLINE MEETING FOUND:")
pprint(
    {
        "id": online_meeting_id,
        "subject": meeting.get("subject"),
        "startDateTime": meeting.get("startDateTime"),
        "endDateTime": meeting.get("endDateTime"),
        "joinWebUrl": meeting.get("joinWebUrl"),
    }
)

print("\nListing transcripts...\n")

transcripts_result = list_meeting_transcripts(
    access_token=access_token,
    online_meeting_id=online_meeting_id,
)

print("\nTRANSCRIPTS RESULT:")
pprint(transcripts_result)

if not transcripts_result.get("success"):
    raise SystemExit

transcripts = transcripts_result.get("data", {}).get("value", [])

if not transcripts:
    print("\nNo transcripts found yet.")
    raise SystemExit

transcript = transcripts[0]
transcript_id = transcript["id"]

print("\nDownloading first transcript...\n")

content_result = download_transcript_content(
    access_token=access_token,
    online_meeting_id=online_meeting_id,
    transcript_id=transcript_id,
)

print("\nCONTENT RESULT:")
pprint(
    {
        "success": content_result.get("success"),
        "status_code": content_result.get("status_code"),
        "preview": content_result.get("text", "")[:1000],
    }
)
