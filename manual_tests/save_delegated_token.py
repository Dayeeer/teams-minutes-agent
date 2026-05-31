from app.auth_token_cache import get_auth_url, save_token_from_auth_code


print("\nOPEN THIS URL:\n")
print(get_auth_url())

print("\nAfter login copy only the value after code=\n")

auth_code = input("Paste authorization code:\n").strip()

result = save_token_from_auth_code(auth_code)

print("\nTOKEN SAVE RESULT:")
print({
    "success": "access_token" in result,
    "account": result.get("id_token_claims", {}).get("preferred_username"),
    "scopes": result.get("scope"),
})

if "access_token" not in result:
    print(result)
