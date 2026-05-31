from auth_service import get_auth_url, authenticate_user
from app.workers.onenote_worker import process_onenote_pages


print("\nOPEN THIS URL:\n")
print(get_auth_url())

print("\nAfter login copy only the value after code=\n")

auth_code = input("Paste authorization code:\n").strip()

auth_result = authenticate_user(auth_code)

print("\nAUTH RESULT SUCCESS:")
print(auth_result.get("success"))

if not auth_result.get("success"):
    print(auth_result)
    raise SystemExit

access_token = auth_result["access_token"]

result = process_onenote_pages(
    access_token=access_token,
    limit=10,
)

print("\nONENOTE WORKER RESULT:")
print(result)
