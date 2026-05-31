from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from microsoft_graph import graph_get


def iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_calendar_view_endpoint(
    days_back: int = 1,
    days_forward: int = 30,
    user_id: str | None = None,
) -> str:
    now = datetime.now(timezone.utc)

    start = iso_utc(now - timedelta(days=days_back))
    end = iso_utc(now + timedelta(days=days_forward))

    start_encoded = quote(start, safe="")
    end_encoded = quote(end, safe="")

    user_prefix = "/me" if user_id is None else f"/users/{quote(user_id, safe='')}"

    return (
        f"{user_prefix}/calendarView"
        f"?startDateTime={start_encoded}"
        f"&endDateTime={end_encoded}"
        "&$top=100"
        "&$orderby=start/dateTime"
        "&$select=id,subject,start,end,organizer,isOnlineMeeting,"
        "onlineMeetingProvider,onlineMeetingUrl,onlineMeeting,webLink"
    )

def list_calendar_events_in_window(
    access_token: str,
    days_back: int = 1,
    days_forward: int = 30,
    user_id: str | None = None,
) -> list[dict]:

    endpoint = build_calendar_view_endpoint(
        days_back=days_back,
        days_forward=days_forward,
        user_id=user_id,
    )

    result = graph_get(
        access_token=access_token,
        endpoint=endpoint,
    )

    if not result.get("success"):
        raise RuntimeError(result)

    return result.get("data", {}).get("value", [])

def get_event_join_url(event: dict) -> str | None:
    if event.get("onlineMeetingUrl"):
        return event["onlineMeetingUrl"]

    online_meeting = event.get("onlineMeeting") or {}

    return online_meeting.get("joinUrl")


def is_supported_teams_event(event: dict) -> bool:
    return (
        event.get("isOnlineMeeting") is True
        and event.get("onlineMeetingProvider") == "teamsForBusiness"
        and bool(get_event_join_url(event))
    )


def extract_calendar_meeting(event: dict) -> dict:
    organizer = (
        event.get("organizer", {})
        .get("emailAddress", {})
        .get("address", "")
    )

    return {
        "calendar_event_id": event.get("id"),
        "subject": event.get("subject"),
        "start_time": event.get("start", {}).get("dateTime"),
        "end_time": event.get("end", {}).get("dateTime"),
        "organizer_email": organizer,
        "is_online_meeting": event.get("isOnlineMeeting"),
        "online_meeting_provider": event.get("onlineMeetingProvider"),
        "join_url": get_event_join_url(event),
        "web_link": event.get("webLink"),
        "status": "calendar_detected",
    }


def discover_teams_meetings_in_window(
    access_token: str,
    days_back: int = 1,
    days_forward: int = 30,
    user_id: str | None = None,
) -> list[dict]:
    events = list_calendar_events_in_window(
        access_token=access_token,
        days_back=days_back,
        days_forward=days_forward,
        user_id=user_id,
    )

    meetings = []

    for event in events:
        if not is_supported_teams_event(event):
            continue

        meetings.append(extract_calendar_meeting(event))

    return meetings


def discover_recent_teams_meetings(access_token: str, limit: int = 20) -> list[dict]:
    # Backward-compatible wrapper for old tests.
    meetings = discover_teams_meetings_in_window(
        access_token=access_token,
        days_back=1,
        days_forward=30,
    )

    return meetings[:limit]
