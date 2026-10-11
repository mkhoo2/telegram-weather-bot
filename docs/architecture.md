# Architecture

## Purpose and stack

This project is a Telegram bot that serves Singapore weather reports and lets subscribers choose a daily report time. The webhook API is Python/FastAPI, data is stored in PostgreSQL through psycopg, outbound HTTP uses `requests`, and scheduled reports use the GitHub Actions workflow in `.github/workflows/weather.yaml`. Weather and air-quality data come from Singapore's NEA/data.gov.sg real-time APIs.

## Components and entry points

- [`main.py`](../main.py) exposes `GET /` as a simple health response and `POST /telegram/webhook` for Telegram updates. It handles `/start`, `/stop`, inline-keyboard callbacks, current weather requests, and custom report-time input.
- [`telegram.py`](../telegram.py) sends messages and acknowledges callback queries through the Telegram Bot API.
- [`database.py`](../database.py) loads environment configuration, opens PostgreSQL connections, creates the `users` table if absent, and provides user subscription, preference, and report-state operations.
- [`weather.py`](../weather.py) calls the NEA/data.gov.sg two-hour forecast, 24-hour forecast, PSI, and PM2.5 endpoints; summarizes the payloads by region; and formats a Telegram report. The compatibility functions `get_weather` and `format_current_weather` delegate to the Singapore-specific implementation.
- [`send_reports.py`](../send_reports.py) is the report batch entry point. It loads subscribed users, fetches shared Singapore weather once per run, checks each user's local time and last-send date, sends due reports, and records the send date.
- [`scheduler.py`](../scheduler.py) defines a standalone APScheduler loop. Repository references do not show it being started by the FastAPI entry point or used by the Actions workflow. Its imports/data handling do not align with the current `weather.py` and `database.py` interfaces; verify or repair it before relying on it.
- [`.github/workflows/weather.yaml`](../.github/workflows/weather.yaml) installs the requirements and runs `send_reports.py` on a 15-minute cron schedule or manual dispatch.

## Data and request flows

### Telegram interaction

Telegram posts updates to `/telegram/webhook`. `/start` subscribes the chat and presents the main menu; `/stop` unsubscribes it. Inline callbacks can request a report or choose a report time. A custom time is accepted as `HH:MM` in 24-hour format and held in a process-local set while the bot waits for the next message. Weather callbacks load the user's stored coordinates and call the weather integration. Current formatting aliases use Singapore-wide weather; stored coordinates are not used by the current weather fetch implementation.

### Database

`database.py` creates a `users` table on module import through `initialize_database()`. The schema is:

| Column | Type | Purpose |
| --- | --- | --- |
| `telegram_id` | `BIGINT PRIMARY KEY` | Telegram chat/user identifier |
| `subscribed` | `BOOLEAN NOT NULL DEFAULT TRUE` | Whether reports are enabled |
| `report_time` | `TEXT NOT NULL DEFAULT '07:00'` | Preferred local send time |
| `timezone` | `TEXT NOT NULL DEFAULT 'Asia/Singapore'` | Time zone used for due checks |
| `latitude`, `longitude` | `DOUBLE PRECISION NOT NULL` | Default location coordinates |
| `last_sent_date` | `TEXT` | Local date of the last report |

Connections use `DATABASE_URL`. Psycopg connection context managers are used for database operations.

### Scheduled reports

The Actions workflow uses the repository's current batch implementation, not `scheduler.py`. `send_reports.py` checks `last_sent_date` to avoid sending more than once per local day and updates it after a successful send. Workflow credentials are provided from the GitHub Actions secrets named `TELEGRAM_BOT_TOKEN` and `DATABASE_URL`.

## Configuration and local development

- `TELEGRAM_BOT_TOKEN`: Telegram Bot API credential.
- `DATABASE_URL`: PostgreSQL connection string.

The modules load `.env` where appropriate through `python-dotenv`; actual values must remain local or in GitHub Actions secrets. [`README.md`](../README.md) documents `uvicorn main:app --reload`, ngrok/webhook setup, and an example local PostgreSQL container.

## Constraints and decisions

- Reports currently use Singapore-wide NEA forecast and air-quality data; `get_weather(latitude, longitude)` accepts coordinates for compatibility but does not use them.
- Custom-time waiting state is in process memory, so it is not shared across multiple API workers or preserved through a restart.
- Importing `main.py` imports `database.py`, which initializes the database immediately; a valid `DATABASE_URL` is therefore required when starting the API.
- Avoid treating `scheduler.py` as operational until its integration and API mismatches are resolved.

## Testing and deployment

No test files, test runner configuration, linter, or build configuration are present in the tracked repository. Dependencies are listed in [`requirements.txt`](../requirements.txt). Local API startup instructions are in the README. Scheduled batch deployment is defined by GitHub Actions and requires the two repository secrets listed above.
