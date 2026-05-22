from templates import (
    build_full_summary_html,
    build_plain_text_summary,
)

summary_html = build_full_summary_html(
    summary_text=(
        "The meeting focused on the architecture of the "
        "AI Meeting Minutes Agent and Microsoft integration."
    ),
    action_items=[
        "Finalize OneNote integration",
        "Implement Outlook draft creation",
        "Prepare workspace architecture",
    ],
    topics=[
        "Microsoft Graph",
        "Workspace isolation",
        "OneNote integration",
    ],
    decisions=[
        "Use fixed OneNote section",
        "Use centralized service account",
    ],
    followups=[
        "Schedule architecture review",
        "Prepare Teams transcript tests",
    ],
    created_by="office@nrgeer.com",
    transcript_language="English",
    summary_mode="Executive Summary",
)

print("\nHTML SUMMARY:\n")
print(summary_html)

plain_text = build_plain_text_summary(
    summary_text=("The meeting focused on AI meeting automation."),
    action_items=[
        "Validate Outlook integration",
        "Improve UI flow",
    ],
)

print("\nPLAIN TEXT SUMMARY:\n")
print(plain_text)
