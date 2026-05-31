from app.meetings.calendar_watcher import discover_teams_meetings_in_window
from app.storage.meetings_v2 import initialize_database, upsert_meeting, count_meetings


def run_calendar_watcher(
    access_token: str,
    days_back: int = 1,
    days_forward: int = 30,
) -> dict:
    initialize_database()

    meetings = discover_teams_meetings_in_window(
        access_token=access_token,
        days_back=days_back,
        days_forward=days_forward,
    )

    saved_count = 0

    for meeting in meetings:
        upsert_meeting(meeting)
        saved_count += 1

    return {
        "success": True,
        "discovered_count": len(meetings),
        "saved_count": saved_count,
        "total_in_db": count_meetings(),
    }
