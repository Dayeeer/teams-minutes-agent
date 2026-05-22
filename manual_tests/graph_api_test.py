from auth_service import (
    get_auth_url,
    authenticate_user,
)

from microsoft_graph import (
    get_current_user,
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

me_result = get_current_user(access_token)

print("\nGRAPH /ME RESULT:\n")
print(me_result)

