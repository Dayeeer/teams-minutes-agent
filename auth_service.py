import msal
import requests

from config import CONFIG
from workspace_manager import validate_workspace_user

SCOPES = [
    "User.Read",
    "Notes.ReadWrite",
    "Mail.ReadWrite",
    "Mail.Send",
    "Calendars.Read",
    "OnlineMeetings.Read",
    "OnlineMeetingTranscript.Read.All",
]

GRAPH_ME_ENDPOINT = "https://graph.microsoft.com/v1.0/me"


def build_msal_app():
    return msal.ConfidentialClientApplication(
        client_id=CONFIG.microsoft.client_id,
        authority=(
            f"https://login.microsoftonline.com/" f"{CONFIG.microsoft.tenant_id}"
        ),
        client_credential=CONFIG.microsoft.client_secret,
    )


def get_auth_url() -> str:
    app = build_msal_app()

    return app.get_authorization_request_url(
        scopes=SCOPES,
        redirect_uri=CONFIG.microsoft.redirect_uri,
        prompt="select_account",
    )


def acquire_token_from_code(auth_code: str) -> dict:
    app = build_msal_app()

    result = app.acquire_token_by_authorization_code(
        code=auth_code,
        scopes=SCOPES,
        redirect_uri=CONFIG.microsoft.redirect_uri,
    )

    return result


def get_graph_headers(access_token: str) -> dict:
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


def get_current_user_profile(access_token: str) -> dict:
    response = requests.get(
        GRAPH_ME_ENDPOINT,
        headers=get_graph_headers(access_token),
    )

    try:
        return response.json()
    except Exception:
        return {
            "error": "Failed to decode Microsoft profile response",
            "status_code": response.status_code,
            "raw_response": response.text,
        }


def extract_user_identity(profile: dict) -> dict:
    email = (
        (profile.get("mail") or profile.get("userPrincipalName") or "").strip().lower()
    )

    return {
        "display_name": profile.get("displayName", ""),
        "email": email,
        "user_id": profile.get("id", ""),
    }


def validate_authenticated_user(profile: dict) -> tuple[bool, str]:
    identity = extract_user_identity(profile)

    email = identity["email"]

    return validate_workspace_user(email)


def authenticate_user(auth_code: str) -> dict:
    token_result = acquire_token_from_code(auth_code)

    if "access_token" not in token_result:
        return {
            "success": False,
            "error": "Microsoft token acquisition failed",
            "details": token_result,
        }

    access_token = token_result["access_token"]

    profile = get_current_user_profile(access_token)

    identity = extract_user_identity(profile)

    is_allowed, message = validate_authenticated_user(profile)

    if not is_allowed:
        return {
            "success": False,
            "error": "User not allowed",
            "message": message,
            "identity": identity,
        }

    return {
        "success": True,
        "access_token": access_token,
        "profile": profile,
        "identity": identity,
        "message": message,
    }

