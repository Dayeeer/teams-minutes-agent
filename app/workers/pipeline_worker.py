from app.workers.calendar_watcher_worker import run_calendar_watcher
from app.workers.transcript_worker import process_calendar_detected_meetings
from app.workers.transcript_download_worker import process_transcript_downloads
from app.workers.summary_worker import process_summaries
from app.workers.onenote_worker import process_onenote_pages


def run_pipeline(
    access_token: str,
    days_back: int = 1,
    days_forward: int = 30,
):
    result = {}

    result["calendar"] = run_calendar_watcher(
        access_token=access_token,
        days_back=days_back,
        days_forward=days_forward,
    )

    result["transcripts"] = process_calendar_detected_meetings(
        access_token=access_token,
        limit=50,
    )

    result["downloads"] = process_transcript_downloads(
        access_token=access_token,
        limit=50,
    )

    result["summaries"] = process_summaries(
        limit=50,
    )

    result["onenote"] = process_onenote_pages(
        access_token=access_token,
        limit=50,
    )

    return result
