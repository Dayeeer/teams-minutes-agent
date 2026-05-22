import os
from dotenv import load_dotenv

from microsoft_auth import (
    get_auth_url,
    acquire_token_by_code,
    get_user_profile,
)

from microsoft_user import (
    extract_user_identity,
    validate_user_access,
)

from onenote_api import (
    get_target_onenote_section,
    create_onenote_page,
)

load_dotenv()

TARGET_NOTEBOOK = os.getenv("ONENOTE_TARGET_NOTEBOOK", "AI Meeting Minutes")
TARGET_SECTION = os.getenv("ONENOTE_TARGET_SECTION", "Meeting Summaries")


print("\nOPEN THIS URL IN YOUR BROWSER:\n")
print(get_auth_url())

print("\nAfter login, copy only the 'code=' value from the browser URL.")
print("Important: copy everything after 'code=' until '&session_state='.\n")

auth_code = input("Paste authorization code here:\n").strip()

token_result = acquire_token_by_code(auth_code)

if "access_token" not in token_result:
    print("\nTOKEN ERROR:\n")
    print(token_result)
    raise SystemExit

access_token = token_result["access_token"]

profile = get_user_profile(access_token)
identity = extract_user_identity(profile)
is_allowed, message = validate_user_access(profile)

print("\nCONNECTED USER:\n")
print(identity)

print("\nACCESS CHECK:\n")
print(message)

if not is_allowed:
    raise SystemExit("Access denied.")

print("\nFinding target OneNote destination...\n")
print(f"Target notebook: {TARGET_NOTEBOOK}")
print(f"Target section: {TARGET_SECTION}")

target, error = get_target_onenote_section(
    access_token=access_token,
    notebook_name=TARGET_NOTEBOOK,
    section_name=TARGET_SECTION,
)

if error:
    print("\nTARGET ERROR:\n")
    print(error)
    raise SystemExit

notebook = target["notebook"]
section = target["section"]

print("\nTARGET FOUND:\n")
print(f"Notebook: {notebook.get('displayName')} | ID: {notebook.get('id')}")
print(f"Section: {section.get('displayName')} | ID: {section.get('id')}")

confirm = input(
    "\nCreate test page in this exact notebook/section? Type YES to confirm:\n"
)

if confirm != "YES":
    print("Cancelled.")
    raise SystemExit

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Targeted OneNote Test Page</title>
</head>
<body>
    <h1>Targeted OneNote Test Page</h1>

    <p>This page was created using the fixed target OneNote destination.</p>

    <h2>Target</h2>
    <ul>
        <li>User: {identity.get("email")}</li>
        <li>Notebook: {notebook.get("displayName")}</li>
        <li>Section: {section.get("displayName")}</li>
    </ul>
</body>
</html>
"""

print("\nCreating OneNote page...\n")

page_status, page_result = create_onenote_page(
    access_token=access_token,
    section_id=section["id"],
    html_content=html_content,
)

print("PAGE STATUS:", page_status)
print("PAGE RESULT:")
print(page_result)

if page_status == 201:
    print("\nSUCCESS: Page created in the fixed target OneNote destination.")
else:
    print("\nFAILED: Page was not created.")
