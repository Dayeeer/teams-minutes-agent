import requests

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


class GraphAPIError(Exception):
    pass


def build_graph_headers(
    access_token: str,
    content_type: str | None = "application/json",
) -> dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    if content_type:
        headers["Content-Type"] = content_type

    return headers


def build_graph_url(endpoint: str) -> str:
    endpoint = endpoint.strip()

    if endpoint.startswith("/"):
        endpoint = endpoint[1:]

    return f"{GRAPH_BASE_URL}/{endpoint}"


def graph_get(
    access_token: str,
    endpoint: str,
) -> dict:
    response = requests.get(
        build_graph_url(endpoint),
        headers=build_graph_headers(access_token),
    )

    return parse_graph_response(response)


def graph_post(
    access_token: str,
    endpoint: str,
    json_data: dict | None = None,
    raw_data: bytes | None = None,
    content_type: str = "application/json",
) -> dict:
    response = requests.post(
        build_graph_url(endpoint),
        headers=build_graph_headers(
            access_token,
            content_type=content_type,
        ),
        json=json_data if raw_data is None else None,
        data=raw_data,
    )

    return parse_graph_response(response)


def parse_graph_response(response) -> dict:
    try:
        data = response.json()
    except Exception:
        data = {"raw_response": response.text}

    result = {
        "success": response.ok,
        "status_code": response.status_code,
        "data": data,
    }

    if not response.ok:
        result["error"] = extract_graph_error(data)

    return result


def extract_graph_error(data: dict) -> str:
    if not isinstance(data, dict):
        return "Unknown Microsoft Graph error"

    error = data.get("error")

    if not error:
        return "Unknown Microsoft Graph error"

    message = error.get("message")

    if message:
        return message

    code = error.get("code")

    if code:
        return code

    return "Unknown Microsoft Graph error"


def get_current_user(access_token: str) -> dict:
    return graph_get(
        access_token=access_token,
        endpoint="/me",
    )


def get_user_onenote_notebooks(access_token: str) -> dict:
    return graph_get(
        access_token=access_token,
        endpoint="/me/onenote/notebooks",
    )


def create_onenote_page(
    access_token: str,
    section_id: str,
    html_content: str,
) -> dict:
    return graph_post(
        access_token=access_token,
        endpoint=f"/me/onenote/sections/{section_id}/pages",
        raw_data=html_content.encode("utf-8"),
        content_type="application/xhtml+xml",
    )


def create_outlook_draft(
    access_token: str,
    subject: str,
    body_html: str,
    to_recipients: list[str],
) -> dict:
    payload = {
        "subject": subject,
        "body": {
            "contentType": "HTML",
            "content": body_html,
        },
        "toRecipients": [
            {"emailAddress": {"address": email}} for email in to_recipients
        ],
    }

    return graph_post(
        access_token=access_token,
        endpoint="/me/messages",
        json_data=payload,
    )
