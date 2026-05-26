from pprint import pprint

from teams_link_parser import (
    parse_teams_meeting_link,
    validate_teams_meeting_link,
)

teams_link = input("Paste Teams meeting link:\n").strip()

result = parse_teams_meeting_link(teams_link)

print("\nPARSED RESULT:\n")
pprint(result)

is_valid, message = validate_teams_meeting_link(teams_link)

print("\nVALIDATION:\n")
print(is_valid, message)

