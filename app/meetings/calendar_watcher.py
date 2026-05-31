from microsoft_graph import graph_get


def list_recent_calendar_events(access_token: str, limit: int = 20) -> list[dict]:
    endpoint = (
        f"/me/events"
        f"?$top={limit}"
        "&$orderby=start/dateTime desc"
        "&$select=id,subject,start,end,organizer,isOnlineMeeting,"
        "onlineMeetingProvider,onlineMeetingUrl,onlineMeeting,webLink"
    )

    result = graph_get(access_token=access_token, endpoint=endpoint)

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


def discover_recent_teams_meetings(access_token: str, limit: int = 20) -> list[dict]:
    events = list_recent_calendar_events(access_token, limit=limit)

    meetings = []

    for event in events:
        if not is_supported_teams_event(event):
            continue

        meetings.append(extract_calendar_meeting(event))

    return meetings
