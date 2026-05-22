from auth_service import (
    get_auth_url,
    authenticate_user,
)

print("\nOPEN THIS URL:\n")
print(get_auth_url())

print("\nAfter login copy only the value after code=\n")

auth_code = input("Paste authorization code:\n").strip()

result = authenticate_user(auth_code)

print("\nRESULT:\n")
print(result)
