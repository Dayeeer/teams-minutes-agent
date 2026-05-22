from microsoft_auth import get_auth_url, acquire_token_by_code, get_user_profile
from microsoft_user import extract_user_identity, validate_user_access

print("\nOPEN THIS URL IN YOUR BROWSER:\n")
print(get_auth_url())

print("\nAfter login, copy the 'code=' parameter from the browser URL.\n")

auth_code = input("Paste authorization code here:\n")

token_result = acquire_token_by_code(auth_code)

access_token = token_result["access_token"]

print("\nTOKEN RESULT:\n")
print(token_result)

if "access_token" in token_result:

    access_token = token_result["access_token"]

    profile = get_user_profile(access_token)

    identity = extract_user_identity(profile)
    is_allowed, message = validate_user_access(profile)

    print("\nUSER IDENTITY:\n")
    print(identity)

    print("\nACCESS CHECK:\n")
    print(message)

    if not is_allowed:
        raise SystemExit("Access denied.")

    print("\nUSER PROFILE:\n")
    print(profile)

else:
    print("\nNO ACCESS TOKEN RETURNED\n")
