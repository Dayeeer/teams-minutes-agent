from microsoft_auth import (
    get_auth_url,
    acquire_token_by_code,
)

from onenote_api import (
    get_onenote_sections,
    create_onenote_page,
)

print("\nOPEN THIS URL IN YOUR BROWSER:\n")
print(get_auth_url())

print("\nAfter login, copy only the 'code=' value from the browser URL.\n")

auth_code = input("Paste authorization code here:\n")

token_result = acquire_token_by_code(auth_code)

if "access_token" not in token_result:
    print("\nTOKEN ERROR:\n")
    print(token_result)
    raise SystemExit

access_token = token_result["access_token"]

print("\nGetting OneNote sections...\n")

status_code, sections_result = get_onenote_sections(access_token)

print("STATUS:", status_code)
print("SECTIONS RESULT:")
print(sections_result)

if status_code != 200:
    raise SystemExit

sections = sections_result.get("value", [])

if not sections:
    print("\nNo OneNote sections found.")
    raise SystemExit

print("\nAvailable sections:\n")

for index, section in enumerate(sections):
    print(f"{index}: {section.get('displayName')} | ID: {section.get('id')}")

section_index = int(input("\nChoose section number:\n"))

section_id = sections[section_index]["id"]

html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Meeting Minutes Test Page</title>
</head>
<body>
    <h1>AI Meeting Minutes Test Page</h1>
    <p>This page was created automatically from Python using Microsoft Graph.</p>

    <h2>Test Summary</h2>
    <ul>
        <li>Microsoft Graph authentication works.</li>
        <li>OneNote API connection works.</li>
        <li>The AI Meeting Minutes Agent can create pages automatically.</li>
    </ul>
</body>
</html>
"""

print("\nCreating OneNote page...\n")

page_status, page_result = create_onenote_page(
    access_token=access_token, section_id=section_id, html_content=html_content
)

print("PAGE STATUS:", page_status)
print("PAGE RESULT:")
print(page_result)
