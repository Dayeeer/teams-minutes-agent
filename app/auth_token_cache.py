from pathlib import Path

import msal

from auth_service import SCOPES
from config import CONFIG


TOKEN_CACHE_PATH = Path("data/msal_token_cache.bin")


def build_token_cache() -> msal.SerializableTokenCache:
    TOKEN_CACHE_PATH.parent.mkdir(exist_ok=True)

    cache = msal.SerializableTokenCache()

    if TOKEN_CACHE_PATH.exists():
        cache.deserialize(TOKEN_CACHE_PATH.read_text())

    return cache


def save_token_cache(cache: msal.SerializableTokenCache):
    if cache.has_state_changed:
        TOKEN_CACHE_PATH.write_text(cache.serialize())


def build_msal_app_with_cache(cache: msal.SerializableTokenCache):
    return msal.ConfidentialClientApplication(
        client_id=CONFIG.microsoft.client_id,
        authority=f"https://login.microsoftonline.com/{CONFIG.microsoft.tenant_id}",
        client_credential=CONFIG.microsoft.client_secret,
        token_cache=cache,
    )


def get_auth_url() -> str:
    cache = build_token_cache()
    app = build_msal_app_with_cache(cache)

    return app.get_authorization_request_url(
        scopes=SCOPES,
        redirect_uri=CONFIG.microsoft.redirect_uri,
        prompt="select_account",
    )


def save_token_from_auth_code(auth_code: str) -> dict:
    cache = build_token_cache()
    app = build_msal_app_with_cache(cache)

    result = app.acquire_token_by_authorization_code(
        code=auth_code,
        scopes=SCOPES,
        redirect_uri=CONFIG.microsoft.redirect_uri,
    )

    save_token_cache(cache)

    return result


def acquire_cached_delegated_token() -> str:
    cache = build_token_cache()
    app = build_msal_app_with_cache(cache)

    accounts = app.get_accounts()

    if not accounts:
        raise RuntimeError(
            "No cached Microsoft account found. Run manual_tests/save_delegated_token.py first."
        )

    result = app.acquire_token_silent(
        scopes=SCOPES,
        account=accounts[0],
    )

    save_token_cache(cache)

    if not result or "access_token" not in result:
        raise RuntimeError(
            f"Failed to acquire cached delegated token. Result: {result}"
        )

    return result["access_token"]
