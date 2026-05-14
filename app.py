import json
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from ai_processor import process_transcript
from templates import render_minutes_html, render_plain_text

load_dotenv()

APP_PASSWORD = os.getenv("APP_PASSWORD", "test123")

st.set_page_config(page_title="AI Meeting Minutes Agent", page_icon="📝", layout="wide")

# --- Session state ---
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


def check_password() -> bool:
    st.sidebar.title("Access")

    password = st.sidebar.text_input("Password", type="password")

    if password == APP_PASSWORD:
        st.session_state.authenticated = True
        return True

    if password:
        st.sidebar.error("Wrong password")

    return st.session_state.authenticated


def load_sample_transcript() -> str:
    try:
        with open("sample_transcript.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def make_safe_filename(title: str) -> str:
    safe_title = "".join(
        c if c.isalnum() or c in (" ", "-", "_") else "_" for c in title
    )
    return safe_title.replace(" ", "_")


if not check_password():
    st.title("AI Meeting Minutes Agent")
    st.info("Enter password in the sidebar to access the MVP.")
    st.stop()


st.title("AI Meeting Minutes Agent MVP")

st.caption(
    "Teams transcript → AI → structured minutes "
    "→ OneNote-style preview → email draft"
)

with st.sidebar:
    st.header("Settings")

    mode = st.selectbox(
        "Processing mode",
        ["Standard Minutes", "Action Items Only", "Executive Summary"],
    )

    create_email = st.checkbox("Prepare email draft if needed", value=True)

    st.divider()

    if st.button("Clear current result"):
        st.session_state.result = None
        st.session_state.html_output = None
        st.session_state.text_output = None
        st.session_state.meeting_title_saved = ""
        st.session_state.mode_saved = ""
        st.rerun()

    st.divider()

    st.write("Current version:\n" "Local MVP without Microsoft Graph")


meeting_title = st.text_input(
    "Meeting title", value="NRGeer / GICA AI Meeting Assistant"
)

use_sample = st.checkbox("Use sample transcript", value=True)

if use_sample:
    transcript_default = load_sample_transcript()
else:
    transcript_default = ""

transcript = st.text_area(
    "Paste Teams transcript here", value=transcript_default, height=350
)

generate = st.button("Generate minutes", type="primary")


if generate:
    if not meeting_title.strip():
        st.error("Please enter a meeting title.")
        st.stop()

    if not transcript.strip():
        st.error("Please paste a transcript.")
        st.stop()

    with st.spinner("Processing transcript with AI..."):
        try:
            result = process_transcript(
                transcript=transcript, meeting_title=meeting_title, mode=mode
            )
        except Exception as e:
            st.error(f"Processing failed:\n\n{e}")
            st.stop()

    html_output = render_minutes_html(result, meeting_title, mode)

    text_output = render_plain_text(result, meeting_title)

    # Save generated output so download buttons do not reset the page
    st.session_state.result = result
    st.session_state.html_output = html_output
    st.session_state.text_output = text_output
    st.session_state.meeting_title_saved = meeting_title
    st.session_state.mode_saved = mode

    st.success("Minutes generated successfully.")


# --- Always show results if they exist ---
if st.session_state.result is not None:
    result = st.session_state.result
    html_output = st.session_state.html_output
    text_output = st.session_state.text_output
    saved_meeting_title = st.session_state.meeting_title_saved
    saved_mode = st.session_state.mode_saved

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    safe_title = make_safe_filename(saved_meeting_title)
    base_filename = f"{timestamp}_{safe_title}"

    tab1, tab2, tab3, tab4 = st.tabs(["Preview", "Email Draft", "JSON", "Downloads"])

    with tab1:
        st.subheader("OneNote-style preview")

        st.components.v1.html(html_output, height=900, scrolling=True)

    with tab2:
        st.subheader("Email draft")

        email = result.get("email_draft", {})

        if create_email and email.get("needed"):
            st.text_input("Subject", value=email.get("subject", ""))

            st.text_area("Body", value=email.get("body", ""), height=300)

        elif create_email:
            st.info("AI decided that no email draft is needed.")

        else:
            st.info("Email draft generation is disabled.")

    with tab3:
        st.subheader("Structured JSON output")
        st.json(result)

    with tab4:
        st.subheader("Download outputs")

        st.download_button(
            label="Download OneNote HTML",
            data=html_output,
            file_name=f"{base_filename}.html",
            mime="text/html",
        )

        st.download_button(
            label="Download plain text minutes",
            data=text_output,
            file_name=f"{base_filename}.txt",
            mime="text/plain",
        )

        st.download_button(
            label="Download JSON",
            data=json.dumps(result, indent=2, ensure_ascii=False),
            file_name=f"{base_filename}.json",
            mime="application/json",
        )

else:
    st.info("Generate minutes to see the preview, email draft, JSON, and downloads.")
