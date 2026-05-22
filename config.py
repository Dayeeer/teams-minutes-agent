import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _get_required_env(name: str) -> str:
    value = os.getenv(name)

    if value is None or not value.strip():
        raise ValueError(f"Missing required environment variable: {name}")

    return value.strip()


def _get_optional_env(name: str, default: str = "") -> str:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip()


def _get_domain_list(name: str) -> list[str]:
    raw_value = _get_optional_env(name)

    return [domain.strip().lower() for domain in raw_value.split(",") if domain.strip()]


@dataclass(frozen=True)
class OpenAIConfig:
    api_key: str
    model: str


@dataclass(frozen=True)
class MicrosoftConfig:
    client_id: str
    tenant_id: str
    client_secret: str
    redirect_uri: str


@dataclass(frozen=True)
class WorkspaceConfig:
    workspace_id: str
    workspace_name: str
    allowed_domains: list[str]
    service_account: str
    mailbox: str
    onenote_notebook: str
    onenote_section: str
    onenote_section_id: str


@dataclass(frozen=True)
class AppConfig:
    app_password: str
    openai: OpenAIConfig
    microsoft: MicrosoftConfig
    workspace: WorkspaceConfig


def load_config() -> AppConfig:
    openai_config = OpenAIConfig(
        api_key=_get_required_env("OPENAI_API_KEY"),
        model=_get_optional_env("OPENAI_MODEL", "gpt-5.4-mini"),
    )

    microsoft_config = MicrosoftConfig(
        client_id=_get_required_env("MICROSOFT_CLIENT_ID"),
        tenant_id=_get_required_env("MICROSOFT_TENANT_ID"),
        client_secret=_get_required_env("MICROSOFT_CLIENT_SECRET"),
        redirect_uri=_get_optional_env(
            "MICROSOFT_REDIRECT_URI",
            "http://localhost:8501",
        ),
    )

    workspace_config = WorkspaceConfig(
        workspace_id=_get_optional_env("WORKSPACE_ID", "nrgeer"),
        workspace_name=_get_optional_env("WORKSPACE_NAME", "NRGeer"),
        allowed_domains=_get_domain_list("WORKSPACE_ALLOWED_DOMAINS"),
        service_account=_get_required_env("WORKSPACE_SERVICE_ACCOUNT").lower(),
        mailbox=_get_required_env("WORKSPACE_MAILBOX").lower(),
        onenote_notebook=_get_optional_env(
            "WORKSPACE_ONENOTE_NOTEBOOK",
            "AI Meeting Minutes",
        ),
        onenote_section=_get_optional_env(
            "WORKSPACE_ONENOTE_SECTION",
            "Meeting Summaries",
        ),
        onenote_section_id=_get_required_env("WORKSPACE_ONENOTE_SECTION_ID"),
    )

    return AppConfig(
        app_password=_get_required_env("APP_PASSWORD"),
        openai=openai_config,
        microsoft=microsoft_config,
        workspace=workspace_config,
    )


CONFIG = load_config()
