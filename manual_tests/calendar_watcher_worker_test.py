from auth_service import get_auth_url, authenticate_user
from app.workers.calendar_watcher_worker import run_calendar_watcher


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

result = run_calendar_watcher(
    access_token=access_token,
    days_back=10,
    days_forward=30,
)

print("\nCALENDAR WATCHER RESULT:")
print(result)
