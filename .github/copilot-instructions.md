# Copilot Instructions

This repository is a Python Telegram bot for Singapore weather. It uses FastAPI for the Telegram webhook, PostgreSQL via psycopg for subscriber preferences, the Singapore NEA/data.gov.sg weather APIs, and Telegram Bot API requests. See [docs/architecture.md](../docs/architecture.md) for the verified component map and data flows.

## Where to look

- `main.py`: FastAPI health route, Telegram webhook, commands, and callback handling.
- `database.py`: PostgreSQL connection, schema initialization, and subscriber operations.
- `weather.py`: NEA API access, weather/air-quality aggregation, and Telegram report formatting.
- `telegram.py`: Telegram Bot API calls.
- `send_reports.py`: scheduled batch report entry point used by GitHub Actions.
- `.github/workflows/weather.yaml`: scheduled/manual report workflow.
- `README.md`: local setup and webhook instructions.

## Working conventions

- Keep changes consistent with the existing small, module-based Python design and direct function-based database and API helpers.
- Read `docs/current-work.md` when continuing prior work; update it at the end of substantial multi-session tasks, not after every minor change.
- Start with the user's requested task; do not automatically perform a full repository scan. Inspect only relevant files and necessary dependencies.
- Reuse existing implementations, utilities, patterns, and dependencies where appropriate. Avoid rereading unchanged files or rediscovering documented architecture without a specific reason.
- For debugging, trace from the relevant entry point through its existing module calls and reproduce the specific failure before changing code.
- Do not run unrelated commands, tests, or analysis. Verify changes with the smallest relevant checks; no test or lint configuration is currently documented.
- Update documentation only when a change materially affects it. Never sacrifice correctness or security merely to save tokens.
- Ask for clarification when a critical requirement is ambiguous. Keep explanations and summaries concise unless more detail is requested.

## Local operation

- Run the API with `uvicorn main:app --reload` (see `README.md` for local PostgreSQL and webhook setup).
- Set `TELEGRAM_BOT_TOKEN` and `DATABASE_URL` in the environment; local `.env` loading is used by the Telegram and database modules. Never read, print, or commit local secrets.
- GitHub Actions runs `python send_reports.py` on its configured schedule and on manual dispatch.
