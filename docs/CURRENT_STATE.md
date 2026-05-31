# Current State

## Repository

Repository: teams-minutes-agent  
Main branch: main

## Current Status

The project currently contains:

- an old flat working implementation in the repository root;
- an archived copy of the old implementation in `legacy/v0_flat_app/`;
- a new modular architecture scaffold in `app/`;
- architectural documentation in `docs/ARCHITECTURE.md`.

## Working Legacy Components

The old implementation includes:

- Microsoft authentication
- Microsoft Graph helper
- Teams link parser
- Teams transcript service
- transcript cleaner
- OpenAI processor
- OneNote service
- Outlook service
- SQLite storage
- Streamlit app / manual workflow

## Known Issues

The old implementation is not yet structured as an autonomous agent.

Main limitations:

- meeting detection is not calendar-first;
- meeting link parsing is too narrow;
- transcript discovery is not robust enough;
- no full meeting lifecycle state machine;
- no automatic OneNote update loop;
- no email thread tracking;
- no production worker structure.

## Next Target

Build the new autonomous architecture step by step:

1. configuration loader
2. Microsoft Graph client
3. calendar watcher
4. meeting database schema
5. meeting lifecycle worker
6. transcript discovery worker
7. summary processor
8. OneNote writer
9. email draft creator
10. email thread tracker
