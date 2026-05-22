from auth_service import (
    get_auth_url,
    authenticate_user,
)

from onenote_service import (
    create_meeting_onenote_page,
)

print("\nOPEN THIS URL:\n")
print(get_auth_url())

print("\nAfter login copy only the value after code=\n")

auth_code = input("Paste authorization code:\n").strip()

auth_result = authenticate_user(auth_code)

print("\nAUTH RESULT:\n")
print(auth_result)

if not auth_result["success"]:
    raise SystemExit

access_token = auth_result["access_token"]

identity = auth_result["identity"]

summary_html = """
<h2>Executive Summary</h2>

<p>
This is a test AI-generated meeting summary.
</p>

<h2>Action Items</h2>

<ul>
    <li>Prepare pilot proposal</li>
    <li>Review Teams integration</li>
    <li>Schedule next meeting</li>
</ul>
"""

result = create_meeting_onenote_page(
    access_token=access_token,
    meeting_title="AI Agent Architecture Discussion",
    summary_html=summary_html,
    created_by=identity["email"],
    transcript_language="English",
    summary_mode="Executive Summary",
    meeting_link="https://teams.microsoft.com/test-link",
)

print("\nONENOTE RESULT:\n")
print(result)
