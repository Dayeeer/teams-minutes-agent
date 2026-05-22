from config import CONFIG


def get_workspace() -> dict:
    workspace = CONFIG.workspace

    return {
        "id": workspace.workspace_id,
        "name": workspace.workspace_name,
        "allowed_domains": workspace.allowed_domains,
        "service_account": workspace.service_account,
        "mailbox": workspace.mailbox,
        "onenote_notebook": workspace.onenote_notebook,
        "onenote_section": workspace.onenote_section,
        "onenote_section_id": workspace.onenote_section_id,
    }


def normalize_email(email: str) -> str:
    return email.strip().lower()


def extract_email_domain(email: str) -> str:
    email = normalize_email(email)

    if "@" not in email:
        return ""

    return email.split("@")[-1]


def is_email_allowed(email: str) -> bool:
    workspace = get_workspace()

    domain = extract_email_domain(email)

    if not domain:
        return False

    return domain in workspace["allowed_domains"]


def is_service_account(email: str) -> bool:
    workspace = get_workspace()

    return normalize_email(email) == workspace["service_account"]


def validate_workspace_user(email: str) -> tuple[bool, str]:
    email = normalize_email(email)

    if not email:
        return False, "No email provided."

    if not is_email_allowed(email):
        return (
            False,
            f"Email {email} is not allowed for this workspace.",
        )

    return (
        True,
        f"Email {email} is allowed for workspace "
        f"{CONFIG.workspace.workspace_name}.",
    )


def get_workspace_onenote_target() -> dict:
    workspace = get_workspace()

    return {
        "notebook_name": workspace["onenote_notebook"],
        "section_name": workspace["onenote_section"],
        "section_id": workspace["onenote_section_id"],
    }


def get_workspace_mailbox() -> str:
    workspace = get_workspace()

    return workspace["mailbox"]


def get_workspace_service_account() -> str:
    workspace = get_workspace()

    return workspace["service_account"]
