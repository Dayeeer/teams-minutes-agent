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
    get_onenote_notebooks,
    get_sections_for_notebook,
    create_onenote_page,
)

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

print("\nGetting OneNote notebooks for this user only...\n")

status_code, notebooks_result = get_onenote_notebooks(access_token)

print("NOTEBOOK STATUS:", status_code)

if status_code != 200:
    print(notebooks_result)
    raise SystemExit

notebooks = notebooks_result.get("value", [])

if not notebooks:
    print("No notebooks found for this user.")
    raise SystemExit

print("\nAvailable notebooks:\n")

for index, notebook in enumerate(notebooks):
    print(f"{index}: {notebook.get('displayName')} | " f"ID: {notebook.get('id')}")

notebook_index = int(input("\nChoose notebook number:\n"))
selected_notebook = notebooks[notebook_index]
notebook_id = selected_notebook["id"]

print(f"\nSelected notebook: {selected_notebook.get('displayName')}\n")

print("Getting sections inside selected notebook only...\n")

section_status, sections_result = get_sections_for_notebook(
    access_token=access_token,
    notebook_id=notebook_id,
)

print("SECTION STATUS:", section_status)

if section_status != 200:
    print(sections_result)
    raise SystemExit

sections = sections_result.get("value", [])

if not sections:
    print("No sections found in this notebook.")
    raise SystemExit

print("\nAvailable sections in selected notebook:\n")

for index, section in enumerate(sections):
    print(f"{index}: {section.get('displayName')} | " f"ID: {section.get('id')}")

section_index = int(input("\nChoose section number:\n"))
selected_section = sections[section_index]
section_id = selected_section["id"]

print(f"\nSelected section: {selected_section.get('displayName')}\n")

confirm = input("Create a test page in this notebook/section? Type YES to confirm:\n")

if confirm != "YES":
    print("Cancelled.")
    raise SystemExit

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Safe OneNote Test Page</title>
</head>
<body>
    <h1>Safe OneNote Test Page</h1>

    <p>This page was created using the safe notebook → section selection flow.</p>

    <h2>Target</h2>
    <ul>
        <li>User: {identity.get("email")}</li>
        <li>Notebook: {selected_notebook.get("displayName")}</li>
        <li>Section: {selected_section.get("displayName")}</li>
    </ul>
</body>
</html>
"""

print("\nCreating OneNote page...\n")

page_status, page_result = create_onenote_page(
    access_token=access_token,
    section_id=section_id,
    html_content=html_content,
)

print("PAGE STATUS:", page_status)
print("PAGE RESULT:")
print(page_result)

if page_status == 201:
    print("\nSUCCESS: Page created in the selected notebook and section.")
else:
    print("\nFAILED: Page was not created.")
