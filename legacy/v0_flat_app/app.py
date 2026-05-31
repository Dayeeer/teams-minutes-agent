import streamlit as st

from config import CONFIG
from workspace_manager import get_workspace
from auth_service import get_auth_url, authenticate_user
from ai_processor import process_meeting_transcript
from transcript_cleaner import clean_transcript, extract_speakers
from templates import build_full_summary_html, build_plain_text_summary
from storage import save_meeting_artifacts
from meeting_manager import (
    initialize_database,
    create_meeting,
    update_meeting_transcript,
    update_transcript_fetch_status,
    update_meeting_summary,
    update_onenote_result,
    update_outlook_result,
    list_recent_meetings,
)
from onenote_service import create_meeting_onenote_page
from outlook_service import create_followup_email_draft
from teams_transcript_service import try_fetch_transcript_from_teams

st.set_page_config(
    page_title="AI Meeting Minutes Agent",
    page_icon="📝",
    layout="wide",
)

initialize_database()


def init_session_state():
    defaults = {
        "authenticated": False,
        "auth_result": None,
        "access_token": None,
        "identity": None,
        "meeting_id": None,
        "meeting_config": None,
        "raw_transcript": "",
        "cleaned_transcript": "",
        "ai_result": None,
        "summary_html": "",
        "plain_text_summary": "",
        "editable_summary_html": "",
        "onenote_result": None,
        "outlook_result": None,
        "storage_result": None,
        "teams_fetch_result": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def check_app_password():
    st.sidebar.subheader("Local Access")

    password = st.sidebar.text_input(
        "App password",
        type="password",
    )

    if password == CONFIG.app_password:
        return True

    if password:
        st.sidebar.error("Wrong password")

    return False


def microsoft_login_ui():
    st.subheader("1. Microsoft Login")

    if st.session_state.authenticated:
        identity = st.session_state.identity
        st.success(f"Connected as {identity.get('email')}")
        return True

    auth_code = st.query_params.get("code")

    if auth_code:
        with st.spinner("Connecting Microsoft account..."):
            result = authenticate_user(auth_code)

        if result.get("success"):
            st.session_state.authenticated = True
            st.session_state.auth_result = result
            st.session_state.access_token = result["access_token"]
            st.session_state.identity = result["identity"]

            st.query_params.clear()
            st.rerun()

        st.error("Microsoft authentication failed.")
        st.json(result)
        return False

    auth_url = get_auth_url()

    st.markdown(
        f"""
        <a href="{auth_url}" target="_self">
            <button style="
                background-color:#2563eb;
                color:white;
                border:none;
                padding:0.7rem 1.2rem;
                border-radius:0.5rem;
                cursor:pointer;
                font-size:1rem;
                font-weight:600;
            ">
                Login with Microsoft
            </button>
        </a>
        """,
        unsafe_allow_html=True,
    )

    st.info("Login using the NRGeer Microsoft account.")
    return False


def meeting_setup_ui():
    st.subheader("2. Meeting Setup")

    col1, col2 = st.columns(2)

    with col1:
        meeting_title = st.text_input(
            "Meeting title",
            value="AI Meeting Minutes",
        )

        meeting_link = st.text_input(
            "Teams meeting link",
            value="",
            placeholder="Paste Teams meeting link here",
        )

    with col2:
        transcript_language = st.selectbox(
            "Output language",
            ["English", "Italian", "German", "Russian"],
            index=0,
        )

        summary_mode = st.selectbox(
            "Summary mode",
            ["Standard Minutes", "Executive Summary", "Action Items Only"],
            index=0,
        )

    special_instructions = st.text_area(
        "Special instructions",
        placeholder=(
            "Example: Focus on decisions, action items, owners, "
            "deadlines and topics requiring follow-up."
        ),
        height=100,
    )

    st.subheader("3. Transcript Source")

    transcript_mode = st.radio(
        "Choose how the transcript should be provided",
        [
            "Automatic Teams transcript check",
            "Manual transcript input",
        ],
        index=0,
    )

    meeting_config = {
        "meeting_title": meeting_title,
        "meeting_link": meeting_link,
        "transcript_language": transcript_language,
        "summary_mode": summary_mode,
        "special_instructions": special_instructions,
        "transcript_mode": transcript_mode,
    }

    st.session_state.meeting_config = meeting_config
    return meeting_config


def create_or_get_meeting_record(meeting_config: dict) -> int:
    if st.session_state.meeting_id:
        return st.session_state.meeting_id

    identity = st.session_state.identity
    workspace = get_workspace()

    transcript_status = (
        "waiting_for_transcript"
        if meeting_config["transcript_mode"] == "Automatic Teams transcript check"
        else "manual_only"
    )

    meeting_id = create_meeting(
        workspace_id=workspace["id"],
        created_by=identity["email"],
        meeting_title=meeting_config["meeting_title"],
        meeting_link=meeting_config["meeting_link"],
        transcript_language=meeting_config["transcript_language"],
        summary_mode=meeting_config["summary_mode"],
        special_instructions=meeting_config["special_instructions"],
        transcript_status=transcript_status,
    )

    st.session_state.meeting_id = meeting_id
    return meeting_id


def show_transcript_preview(transcript_text: str):
    cleaned = clean_transcript(transcript_text)
    speakers = extract_speakers(cleaned)

    st.session_state.raw_transcript = transcript_text
    st.session_state.cleaned_transcript = cleaned

    st.caption(
        f"Raw length: {len(transcript_text)} chars | "
        f"Cleaned length: {len(cleaned)} chars"
    )

    if speakers:
        st.caption(f"Detected speakers: {', '.join(speakers)}")

    with st.expander("Preview cleaned transcript"):
        st.text_area(
            "Cleaned transcript",
            value=cleaned,
            height=250,
        )


def automatic_transcript_ui(meeting_config: dict):
    st.subheader("Automatic Teams Transcript")

    st.info(
        "The meeting must be finished and transcription must have been enabled. "
        "The service account should be invited to the meeting."
    )

    if not meeting_config["meeting_link"].strip():
        st.warning("Paste the Teams meeting link first.")
        return ""

    meeting_id = create_or_get_meeting_record(meeting_config)

    if st.button("Check Teams transcript now", type="primary"):
        with st.spinner("Checking Teams transcript..."):
            result = try_fetch_transcript_from_teams(
                access_token=st.session_state.access_token,
                meeting_link=meeting_config["meeting_link"],
            )

        st.session_state.teams_fetch_result = result

        if result.get("success"):
            transcript_content = result.get("content", "")

            update_transcript_fetch_status(
                meeting_id=meeting_id,
                transcript_status="transcript_downloaded",
                transcript_text=transcript_content,
            )

            st.session_state.raw_transcript = transcript_content
            st.success("Transcript downloaded from Teams.")
            show_transcript_preview(transcript_content)
            return transcript_content

        update_transcript_fetch_status(
            meeting_id=meeting_id,
            transcript_status=result.get("status", "auto_fetch_failed"),
        )

        st.warning(result.get("message", "Transcript not available yet."))

        with st.expander("Technical details"):
            st.json(result)

    if st.session_state.raw_transcript:
        show_transcript_preview(st.session_state.raw_transcript)
        return st.session_state.raw_transcript

    return ""


def manual_transcript_input_ui():
    st.subheader("Manual Transcript Input")

    input_mode = st.radio(
        "Manual transcript input method",
        [
            "Paste transcript manually",
            "Upload transcript file",
            "Use sample transcript",
        ],
    )

    transcript_text = ""

    if input_mode == "Paste transcript manually":
        transcript_text = st.text_area(
            "Paste Teams transcript here",
            height=300,
        )

    elif input_mode == "Upload transcript file":
        uploaded_file = st.file_uploader(
            "Upload .txt or .vtt file",
            type=["txt", "vtt"],
        )

        if uploaded_file:
            transcript_text = uploaded_file.read().decode(
                "utf-8",
                errors="ignore",
            )

    else:
        try:
            with open("sample_transcript.txt", "r", encoding="utf-8") as file:
                transcript_text = file.read()
        except FileNotFoundError:
            st.error("sample_transcript.txt not found.")

    if transcript_text:
        show_transcript_preview(transcript_text)

    return transcript_text


def generate_summary(meeting_config: dict, transcript_text: str):
    meeting_id = create_or_get_meeting_record(meeting_config)

    cleaned_transcript = clean_transcript(transcript_text)

    update_meeting_transcript(
        meeting_id=meeting_id,
        transcript_text=cleaned_transcript,
        transcript_status=(
            "auto_downloaded"
            if meeting_config["transcript_mode"] == "Automatic Teams transcript check"
            else "manual_uploaded"
        ),
    )

    ai_result = process_meeting_transcript(
        transcript=cleaned_transcript,
        meeting_title=meeting_config["meeting_title"],
        transcript_language=meeting_config["transcript_language"],
        summary_mode=meeting_config["summary_mode"],
        special_instructions=meeting_config["special_instructions"],
    )

    identity = st.session_state.identity

    summary_html = build_full_summary_html(
        summary_text=ai_result.get("summary", ""),
        action_items=ai_result.get("action_items", []),
        topics=ai_result.get("topics", []),
        decisions=ai_result.get("decisions", []),
        followups=ai_result.get("followups", []),
        created_by=identity["email"],
        transcript_language=meeting_config["transcript_language"],
        summary_mode=meeting_config["summary_mode"],
    )

    plain_text = build_plain_text_summary(
        summary_text=ai_result.get("summary", ""),
        action_items=ai_result.get("action_items", []),
    )

    update_meeting_summary(
        meeting_id=meeting_id,
        summary_html=summary_html,
    )

    st.session_state.ai_result = ai_result
    st.session_state.summary_html = summary_html
    st.session_state.plain_text_summary = plain_text
    st.session_state.editable_summary_html = summary_html

    return ai_result


def result_review_ui():
    if not st.session_state.ai_result:
        return

    st.subheader("4. Review & Edit")

    tab1, tab2, tab3 = st.tabs(["Editable HTML", "Structured JSON", "Plain Text"])

    with tab1:
        st.session_state.editable_summary_html = st.text_area(
            "Editable summary HTML",
            value=st.session_state.editable_summary_html,
            height=450,
        )

    with tab2:
        st.json(st.session_state.ai_result)

    with tab3:
        st.text_area(
            "Plain text summary",
            value=st.session_state.plain_text_summary,
            height=300,
        )


def export_actions_ui(meeting_config: dict):
    if not st.session_state.ai_result:
        return

    st.subheader("5. Save / Export")

    access_token = st.session_state.access_token
    identity = st.session_state.identity
    meeting_id = st.session_state.meeting_id
    edited_html = st.session_state.editable_summary_html

    recipients_raw = st.text_input(
        "Email draft recipients, comma-separated",
        value=identity["email"],
    )

    recipients = [email.strip() for email in recipients_raw.split(",") if email.strip()]

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Save locally"):
            storage_result = save_meeting_artifacts(
                meeting_title=meeting_config["meeting_title"],
                html_summary=edited_html,
                text_summary=st.session_state.plain_text_summary,
                ai_result=st.session_state.ai_result,
            )

            st.session_state.storage_result = storage_result
            st.success("Saved locally.")
            st.json(storage_result)

    with col2:
        if st.button("Create OneNote page"):
            result = create_meeting_onenote_page(
                access_token=access_token,
                meeting_title=meeting_config["meeting_title"],
                summary_html=edited_html,
                created_by=identity["email"],
                transcript_language=meeting_config["transcript_language"],
                summary_mode=meeting_config["summary_mode"],
                meeting_link=meeting_config["meeting_link"],
            )

            st.session_state.onenote_result = result

            if result.get("success"):
                update_onenote_result(
                    meeting_id=meeting_id,
                    onenote_page_url=result.get("onenote_url") or "",
                    onenote_page_id=result.get("page_id") or "",
                )

                st.success("OneNote page created.")

                if result.get("onenote_url"):
                    st.markdown(f"[Open OneNote page]({result['onenote_url']})")
            else:
                st.error("Failed to create OneNote page.")
                st.json(result)

    with col3:
        if st.button("Create Outlook draft"):
            result = create_followup_email_draft(
                access_token=access_token,
                meeting_title=meeting_config["meeting_title"],
                summary_html=edited_html,
                created_by=identity["email"],
                recipients=recipients,
                meeting_link=meeting_config["meeting_link"],
            )

            st.session_state.outlook_result = result

            if result.get("success"):
                update_outlook_result(
                    meeting_id=meeting_id,
                    draft_id=result.get("draft_id") or "",
                    draft_subject=result.get("subject") or "",
                )

                st.success("Outlook draft created.")

                if result.get("web_link"):
                    st.markdown(f"[Open Outlook draft]({result['web_link']})")
            else:
                st.error("Failed to create Outlook draft.")
                st.json(result)


def sidebar_ui():
    workspace = get_workspace()

    st.sidebar.title("AI Meeting Agent")

    st.sidebar.subheader("Workspace")
    st.sidebar.write(workspace["name"])
    st.sidebar.caption(f"Service account: {workspace['service_account']}")
    st.sidebar.caption(
        f"OneNote: {workspace['onenote_notebook']} → " f"{workspace['onenote_section']}"
    )

    if st.session_state.authenticated:
        st.sidebar.success(f"Connected: {st.session_state.identity['email']}")

    if st.sidebar.button("Reset current session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.sidebar.divider()

    st.sidebar.subheader("Recent Meetings")

    try:
        recent_meetings = list_recent_meetings(limit=10)

        if not recent_meetings:
            st.sidebar.caption("No meetings yet.")

        for meeting in recent_meetings:
            st.sidebar.caption(
                f"#{meeting['id']} | "
                f"{meeting['meeting_title']} | "
                f"{meeting['status']} | "
                f"{meeting.get('transcript_status')}"
            )

    except Exception:
        st.sidebar.caption("Meeting history unavailable.")


def main():
    init_session_state()

    if not check_app_password():
        st.title("AI Meeting Minutes Agent")
        st.info("Enter the local app password in the sidebar.")
        return

    sidebar_ui()

    st.title("AI Meeting Minutes Agent")
    st.caption("Teams transcript → AI minutes → OneNote page → Outlook draft")

    microsoft_ready = microsoft_login_ui()

    if not microsoft_ready:
        return

    meeting_config = meeting_setup_ui()

    if meeting_config["transcript_mode"] == "Automatic Teams transcript check":
        transcript_text = automatic_transcript_ui(meeting_config)
    else:
        transcript_text = manual_transcript_input_ui()

    st.divider()

    if st.button("Generate AI Meeting Minutes", type="primary"):
        if not meeting_config["meeting_title"].strip():
            st.error("Meeting title is required.")
            return

        if not transcript_text.strip():
            st.error(
                "Transcript is required. Fetch it from Teams or provide it manually."
            )
            return

        with st.spinner("Processing transcript with AI..."):
            try:
                generate_summary(
                    meeting_config=meeting_config,
                    transcript_text=transcript_text,
                )
            except Exception as error:
                st.error("AI processing failed.")
                st.exception(error)
                return

        st.success("AI meeting minutes generated.")

    result_review_ui()
    export_actions_ui(meeting_config=meeting_config)


if __name__ == "__main__":
    main()
