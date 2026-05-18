import html
import json
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from ai_processor import process_transcript
from templates import render_minutes_html, render_plain_text
from transcript_cleaner import clean_transcript, estimate_transcript_stats
from storage import save_outputs_locally
from meeting_manager import (
    init_db,
    create_meeting,
    list_meetings,
    update_meeting_status,
    update_meeting_outputs,
    delete_meeting,
)

load_dotenv()

APP_PASSWORD = os.getenv("APP_PASSWORD", "test123")

st.set_page_config(
    page_title="AI Meeting Minutes Agent",
    page_icon="📝",
    layout="wide",
)

init_db()


# ---------------------------
# SESSION STATE
# ---------------------------

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "result" not in st.session_state:
    st.session_state.result = None

if "html_output" not in st.session_state:
    st.session_state.html_output = None

if "text_output" not in st.session_state:
    st.session_state.text_output = None

if "meeting_title_saved" not in st.session_state:
    st.session_state.meeting_title_saved = ""

if "mode_saved" not in st.session_state:
    st.session_state.mode_saved = ""

if "output_language_saved" not in st.session_state:
    st.session_state.output_language_saved = "English"

if "saved_file_paths" not in st.session_state:
    st.session_state.saved_file_paths = None

if "edited_text_output" not in st.session_state:
    st.session_state.edited_text_output = ""

if "edited_email_subject" not in st.session_state:
    st.session_state.edited_email_subject = ""

if "edited_email_body" not in st.session_state:
    st.session_state.edited_email_body = ""


# ---------------------------
# HELPER FUNCTIONS
# ---------------------------


def check_password() -> bool:
    st.sidebar.title("Access")

    password = st.sidebar.text_input(
        "Password",
        type="password",
    )

    if password == APP_PASSWORD:
        st.session_state.authenticated = True
        return True

    if password:
        st.sidebar.error("Wrong password")

    return st.session_state.authenticated


def load_sample_transcript() -> str:
    try:
        with open(
            "sample_transcript.txt",
            "r",
            encoding="utf-8",
        ) as f:
            return f.read()
    except FileNotFoundError:
        return ""


def make_safe_filename(title: str) -> str:
    safe_title = "".join(
        c if c.isalnum() or c in (" ", "-", "_") else "_" for c in title
    )
    return safe_title.replace(" ", "_")


def render_edited_text_as_html(title: str, edited_text: str) -> str:
    escaped_title = html.escape(title)
    escaped_text = html.escape(edited_text).replace("\n", "<br>")

    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{escaped_title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.5;
            color: #222;
        }}
        h1 {{
            color: #1f4e79;
        }}
        .content {{
            white-space: normal;
        }}
    </style>
</head>
<body>
    <h1>{escaped_title}</h1>
    <div class="content">
        {escaped_text}
    </div>
</body>
</html>
"""


def get_transcript_from_input(
    input_key_prefix: str,
    default_to_sample: bool = False,
) -> str:
    input_options = [
        "Paste transcript manually",
        "Upload transcript file",
    ]

    if default_to_sample:
        input_options.insert(0, "Use sample transcript")

    input_method = st.radio(
        "Choose transcript input method",
        input_options,
        key=f"{input_key_prefix}_input_method",
    )

    transcript_default = ""

    if input_method == "Use sample transcript":
        transcript_default = load_sample_transcript()

    elif input_method == "Upload transcript file":
        uploaded_file = st.file_uploader(
            "Upload Teams transcript file",
            type=["txt", "vtt"],
            key=f"{input_key_prefix}_file_uploader",
        )

        if uploaded_file is not None:
            transcript_default = uploaded_file.read().decode(
                "utf-8",
                errors="ignore",
            )

    transcript = st.text_area(
        "Transcript text",
        value=transcript_default,
        height=300,
        key=f"{input_key_prefix}_transcript_text",
    )

    return transcript


def prepare_transcript_for_ai(
    transcript: str,
    clean_before_processing: bool,
    show_cleaned_preview: bool,
    key_prefix: str,
) -> str:
    cleaned_transcript = clean_transcript(transcript)

    if clean_before_processing:
        transcript_for_ai = cleaned_transcript
    else:
        transcript_for_ai = transcript

    stats = estimate_transcript_stats(transcript, cleaned_transcript)

    st.caption(
        f"Transcript length: {stats['raw_chars']} characters | "
        f"Cleaned: {stats['cleaned_chars']} characters | "
        f"Reduction: {stats['reduction_percent']}%"
    )

    if show_cleaned_preview:
        st.text_area(
            "Cleaned transcript preview",
            value=cleaned_transcript,
            height=220,
            key=f"{key_prefix}_cleaned_preview",
        )

    return transcript_for_ai


def run_ai_pipeline(
    transcript_for_ai: str,
    meeting_title: str,
    mode: str,
    output_language: str,
    special_instructions: str,
    save_locally: bool,
):
    result = process_transcript(
        transcript=transcript_for_ai,
        meeting_title=meeting_title,
        mode=mode,
        output_language=output_language,
        special_instructions=special_instructions,
    )

    html_output = render_minutes_html(
        result,
        meeting_title,
        mode,
        output_language,
    )

    text_output = render_plain_text(
        result,
        meeting_title,
        output_language,
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    if save_locally:
        saved_file_paths = save_outputs_locally(
            meeting_title=meeting_title,
            timestamp=timestamp,
            html_output=html_output,
            text_output=text_output,
            json_output=result,
        )
    else:
        saved_file_paths = None

    st.session_state.result = result
    st.session_state.html_output = html_output
    st.session_state.text_output = text_output
    st.session_state.meeting_title_saved = meeting_title
    st.session_state.mode_saved = mode
    st.session_state.output_language_saved = output_language
    st.session_state.saved_file_paths = saved_file_paths

    email = result.get("email_draft", {})

    st.session_state.edited_text_output = text_output
    st.session_state.edited_email_subject = email.get("subject", "")
    st.session_state.edited_email_body = email.get("body", "")

    return result, html_output, text_output, saved_file_paths


def show_results(create_email: bool):
    if st.session_state.result is None:
        st.info(
            "Generate minutes to see the preview, editable output, email draft, JSON, and downloads."
        )
        return

    result = st.session_state.result
    html_output = st.session_state.html_output
    text_output = st.session_state.text_output
    saved_meeting_title = st.session_state.meeting_title_saved
    saved_file_paths = st.session_state.saved_file_paths

    if saved_file_paths:
        st.success("Outputs saved locally.")
        st.write(saved_file_paths)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    safe_title = make_safe_filename(saved_meeting_title)
    base_filename = f"{timestamp}_{safe_title}"

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Preview",
            "Editable Output",
            "Email Draft",
            "JSON",
            "Downloads",
        ]
    )

    with tab1:
        st.subheader("OneNote-style preview")

        st.components.v1.html(
            html_output,
            height=900,
            scrolling=True,
        )

    with tab2:
        st.subheader("Editable final minutes")

        st.info(
            "You can manually edit the final minutes here. "
            "The edited version will be used for edited TXT/HTML downloads."
        )

        st.session_state.edited_text_output = st.text_area(
            "Final meeting minutes",
            value=st.session_state.edited_text_output or text_output,
            height=500,
        )

    with tab3:
        st.subheader("Editable email draft")

        email = result.get("email_draft", {})

        if create_email and email.get("needed"):
            st.session_state.edited_email_subject = st.text_input(
                "Subject",
                value=st.session_state.edited_email_subject or email.get("subject", ""),
            )

            st.session_state.edited_email_body = st.text_area(
                "Body",
                value=st.session_state.edited_email_body or email.get("body", ""),
                height=300,
            )

        elif create_email:
            st.info("AI decided that no email draft is needed.")

            st.session_state.edited_email_subject = st.text_input(
                "Manual email subject",
                value=st.session_state.edited_email_subject,
            )

            st.session_state.edited_email_body = st.text_area(
                "Manual email body",
                value=st.session_state.edited_email_body,
                height=250,
            )

        else:
            st.info("Email draft generation is disabled.")

    with tab4:
        st.subheader("Structured JSON output")
        st.json(result)

    with tab5:
        st.subheader("Download outputs")

        edited_text = st.session_state.edited_text_output or text_output

        edited_html_output = render_edited_text_as_html(
            saved_meeting_title,
            edited_text,
        )

        edited_email_export = (
            f"Subject: {st.session_state.edited_email_subject}\n\n"
            f"{st.session_state.edited_email_body}"
        )

        st.download_button(
            label="Download original OneNote HTML",
            data=html_output,
            file_name=f"{base_filename}_original.html",
            mime="text/html",
        )

        st.download_button(
            label="Download edited HTML",
            data=edited_html_output,
            file_name=f"{base_filename}_edited.html",
            mime="text/html",
        )

        st.download_button(
            label="Download edited plain text minutes",
            data=edited_text,
            file_name=f"{base_filename}_edited.txt",
            mime="text/plain",
        )

        st.download_button(
            label="Download email draft",
            data=edited_email_export,
            file_name=f"{base_filename}_email_draft.txt",
            mime="text/plain",
        )

        st.download_button(
            label="Download JSON",
            data=json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            ),
            file_name=f"{base_filename}.json",
            mime="application/json",
        )


# ---------------------------
# AUTH
# ---------------------------

if not check_password():
    st.title("AI Meeting Minutes Agent")
    st.info("Enter password in the sidebar to access the MVP.")
    st.stop()


# ---------------------------
# MAIN APP
# ---------------------------

st.title("AI Meeting Minutes Agent MVP")

st.caption(
    "Register meetings → process Teams transcripts → generate structured minutes → save outputs"
)


with st.sidebar:
    st.header("Global settings")

    clean_before_processing = st.checkbox(
        "Clean transcript before processing",
        value=True,
    )

    show_cleaned_preview = st.checkbox(
        "Show cleaned transcript preview",
        value=False,
    )

    save_locally = st.checkbox(
        "Save outputs locally",
        value=True,
    )

    st.divider()

    if st.button("Clear current result"):
        st.session_state.result = None
        st.session_state.html_output = None
        st.session_state.text_output = None
        st.session_state.meeting_title_saved = ""
        st.session_state.mode_saved = ""
        st.session_state.output_language_saved = "English"
        st.session_state.saved_file_paths = None
        st.session_state.edited_text_output = ""
        st.session_state.edited_email_subject = ""
        st.session_state.edited_email_body = ""
        st.rerun()

    st.divider()

    st.write("Current version:\n" "Meeting registration layer without Microsoft Graph")


main_tab_1, main_tab_2, main_tab_3 = st.tabs(
    [
        "Quick Process",
        "Register Meeting",
        "Meetings Dashboard",
    ]
)


# ---------------------------
# TAB 1 — QUICK PROCESS
# ---------------------------

with main_tab_1:
    st.header("Quick Process")

    st.write(
        "Use this for direct transcript processing without registering a meeting first."
    )

    quick_meeting_title = st.text_input(
        "Meeting title",
        value="NRGeer / GICA AI Meeting Assistant",
        key="quick_meeting_title",
    )

    quick_mode = st.selectbox(
        "Processing mode",
        [
            "Standard Minutes",
            "Action Items Only",
            "Executive Summary",
        ],
        key="quick_mode",
    )

    quick_output_language = st.selectbox(
        "Output language",
        [
            "English",
            "Italian",
            "German",
            "Russian",
        ],
        key="quick_output_language",
    )

    quick_create_email = st.checkbox(
        "Prepare email draft if needed",
        value=True,
        key="quick_create_email",
    )

    quick_special_instructions = st.text_area(
        "Special instructions for this meeting",
        placeholder=(
            "Example: Focus mainly on action items. "
            "Create a short follow-up email only if there are urgent decisions."
        ),
        height=100,
        key="quick_special_instructions",
    )

    st.subheader("Transcript input")

    quick_transcript = get_transcript_from_input(
        input_key_prefix="quick",
        default_to_sample=True,
    )

    quick_transcript_for_ai = prepare_transcript_for_ai(
        transcript=quick_transcript,
        clean_before_processing=clean_before_processing,
        show_cleaned_preview=show_cleaned_preview,
        key_prefix="quick",
    )

    if st.button("Generate minutes", type="primary", key="quick_generate"):
        if not quick_meeting_title.strip():
            st.error("Please enter a meeting title.")
            st.stop()

        if not quick_transcript_for_ai.strip():
            st.error("Please paste or upload a valid transcript.")
            st.stop()

        with st.spinner("Processing transcript with AI..."):
            try:
                run_ai_pipeline(
                    transcript_for_ai=quick_transcript_for_ai,
                    meeting_title=quick_meeting_title,
                    mode=quick_mode,
                    output_language=quick_output_language,
                    special_instructions=quick_special_instructions,
                    save_locally=save_locally,
                )
            except Exception as e:
                st.error(f"Processing failed:\n\n{e}")
                st.stop()

        st.success("Minutes generated successfully.")

    show_results(create_email=quick_create_email)


# ---------------------------
# TAB 2 — REGISTER MEETING
# ---------------------------

with main_tab_2:
    st.header("Register Meeting")

    st.write(
        "Use this before a meeting. Later, after the Teams transcript is available, "
        "you can process it from the dashboard using the saved settings."
    )

    with st.form("register_meeting_form"):
        reg_meeting_title = st.text_input(
            "Meeting title",
            value="",
            placeholder="Example: Weekly AI Agent Project Meeting",
        )

        reg_meeting_link = st.text_area(
            "Teams meeting link",
            value="",
            placeholder="Paste the Teams meeting link here",
            height=100,
        )

        reg_mode = st.selectbox(
            "Processing mode",
            [
                "Standard Minutes",
                "Action Items Only",
                "Executive Summary",
            ],
        )

        reg_output_language = st.selectbox(
            "Output language",
            [
                "English",
                "Italian",
                "German",
                "Russian",
            ],
        )

        reg_create_email = st.checkbox(
            "Prepare email draft if needed",
            value=True,
        )

        reg_special_instructions = st.text_area(
            "Special instructions",
            placeholder=(
                "Example: Focus on decisions, responsibilities and urgent follow-ups."
            ),
            height=120,
        )

        submitted = st.form_submit_button("Register meeting")

        if submitted:
            if not reg_meeting_title.strip():
                st.error("Meeting title is required.")
            else:
                meeting_id = create_meeting(
                    meeting_title=reg_meeting_title.strip(),
                    meeting_link=reg_meeting_link.strip(),
                    mode=reg_mode,
                    output_language=reg_output_language,
                    special_instructions=reg_special_instructions.strip(),
                    create_email=reg_create_email,
                )

                st.success(f"Meeting registered successfully. ID: {meeting_id}")


# ---------------------------
# TAB 3 — MEETINGS DASHBOARD
# ---------------------------

with main_tab_3:
    st.header("Meetings Dashboard")

    meetings = list_meetings()

    if not meetings:
        st.info("No registered meetings yet.")
    else:
        st.subheader("Registered meetings")

        for meeting in meetings:
            title = meeting["meeting_title"]
            status = meeting["status"]
            meeting_id = meeting["id"]

            with st.expander(
                f"#{meeting_id} | {title} | Status: {status}",
                expanded=False,
            ):
                st.write(f"**Created:** {meeting['created_at']}")
                st.write(f"**Updated:** {meeting['updated_at']}")
                st.write(f"**Mode:** {meeting['mode']}")
                st.write(f"**Output language:** {meeting['output_language']}")
                st.write(
                    f"**Create email draft:** {'Yes' if meeting['create_email'] else 'No'}"
                )

                if meeting["meeting_link"]:
                    st.write("**Meeting link:**")
                    st.code(meeting["meeting_link"])

                if meeting["special_instructions"]:
                    st.write("**Special instructions:**")
                    st.write(meeting["special_instructions"])

                if meeting["output_html_path"]:
                    st.write("**Saved outputs:**")
                    st.write(
                        {
                            "html": meeting["output_html_path"],
                            "txt": meeting["output_txt_path"],
                            "json": meeting["output_json_path"],
                        }
                    )

                st.divider()

                st.subheader("Process this meeting")

                meeting_transcript = get_transcript_from_input(
                    input_key_prefix=f"meeting_{meeting_id}",
                    default_to_sample=False,
                )

                meeting_transcript_for_ai = prepare_transcript_for_ai(
                    transcript=meeting_transcript,
                    clean_before_processing=clean_before_processing,
                    show_cleaned_preview=show_cleaned_preview,
                    key_prefix=f"meeting_{meeting_id}",
                )

                col1, col2 = st.columns(2)

                with col1:
                    process_clicked = st.button(
                        "Process meeting",
                        type="primary",
                        key=f"process_meeting_{meeting_id}",
                    )

                with col2:
                    delete_clicked = st.button(
                        "Delete meeting",
                        key=f"delete_meeting_{meeting_id}",
                    )

                if process_clicked:
                    if not meeting_transcript_for_ai.strip():
                        st.error("Please paste or upload a valid transcript.")
                        st.stop()

                    update_meeting_status(meeting_id, "processing")

                    with st.spinner("Processing registered meeting with AI..."):
                        try:
                            _, _, _, saved_paths = run_ai_pipeline(
                                transcript_for_ai=meeting_transcript_for_ai,
                                meeting_title=meeting["meeting_title"],
                                mode=meeting["mode"],
                                output_language=meeting["output_language"],
                                special_instructions=meeting["special_instructions"]
                                or "",
                                save_locally=save_locally,
                            )

                            if saved_paths:
                                update_meeting_outputs(
                                    meeting_id=meeting_id,
                                    html_path=saved_paths.get("html"),
                                    txt_path=saved_paths.get("txt"),
                                    json_path=saved_paths.get("json"),
                                )
                            else:
                                update_meeting_outputs(
                                    meeting_id=meeting_id,
                                    html_path=None,
                                    txt_path=None,
                                    json_path=None,
                                )

                        except Exception as e:
                            update_meeting_status(meeting_id, "failed")
                            st.error(f"Processing failed:\n\n{e}")
                            st.stop()

                    st.success("Registered meeting processed successfully.")
                    st.rerun()

                if delete_clicked:
                    delete_meeting(meeting_id)
                    st.success("Meeting deleted.")
                    st.rerun()

        st.divider()
        st.subheader("Latest generated result")
        show_results(create_email=True)
