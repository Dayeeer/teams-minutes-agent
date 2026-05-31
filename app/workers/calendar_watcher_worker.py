from app.meetings.calendar_watcher import discover_recent_teams_meetings
from app.storage.meetings_v2 import initialize_database, upsert_meeting, count_meetings


def run_calendar_watcher(access_token: str, limit: int = 20) -> dict:
    initialize_database()

    meetings = discover_recent_teams_meetings(
        access_token=access_token,
        limit=limit,
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
