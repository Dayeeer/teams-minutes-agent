from auth_service import get_auth_url, authenticate_user
from microsoft_graph import graph_get


def print_event(event: dict, index: int):
    subject = event.get("subject", "(no subject)")
    start = event.get("start", {}).get("dateTime", "")
    end = event.get("end", {}).get("dateTime", "")
    organizer = (
        event.get("organizer", {})
        .get("emailAddress", {})
        .get("address", "")
    )
    is_online = event.get("isOnlineMeeting")
    online_provider = event.get("onlineMeetingProvider")
    join_url = event.get("onlineMeetingUrl")
    event_id = event.get("id")

    print("\n" + "=" * 80)
    print(f"EVENT #{index}")
    print("=" * 80)
    print(f"Subject: {subject}")
    print(f"Start: {start}")
    print(f"End: {end}")
    print(f"Organizer: {organizer}")
    print(f"Is online meeting: {is_online}")
    print(f"Online provider: {online_provider}")
    print(f"Event ID: {event_id}")

    if join_url:
        print(f"Join URL: {join_url[:250]}...")


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

endpoint = (
    "/me/events"
    "?$top=10"
    "&$orderby=start/dateTime desc"
    "&$select=id,subject,start,end,organizer,isOnlineMeeting,onlineMeetingProvider,onlineMeetingUrl,webLink"
)

events_result = graph_get(
    access_token=access_token,
    endpoint=endpoint,
)

print("\nCALENDAR EVENTS RESULT SUCCESS:")
print(events_result.get("success"))

if not events_result.get("success"):
    print(events_result)
    raise SystemExit

events = events_result.get("data", {}).get("value", [])

print(f"\nFound {len(events)} events.\n")

for index, event in enumerate(events, start=1):
    print_event(event, index)
