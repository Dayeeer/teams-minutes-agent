import msal

from config import CONFIG
from app.workers.pipeline_worker import run_pipeline


def acquire_app_token() -> str:
    app = msal.ConfidentialClientApplication(
        client_id=CONFIG.microsoft.client_id,
        authority=f"https://login.microsoftonline.com/{CONFIG.microsoft.tenant_id}",
        client_credential=CONFIG.microsoft.client_secret,
    )

    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )

    if "access_token" not in result:
        raise RuntimeError(result)

    return result["access_token"]


def main():
    access_token = acquire_app_token()

    result = run_pipeline(
        access_token=access_token,
        days_back=1,
        days_forward=30,
        user_id=CONFIG.workspace.service_account,
    )

    print(result)

if __name__ == "__main__":
    main()
