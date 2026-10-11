# Current Work

## Current project status

The repository contains a FastAPI Telegram webhook and a GitHub Actions batch workflow for daily weather reports. No active feature work is documented.

## Active work

No active task has been documented.

## Important decisions and constraints

- The active scheduled-report path is `send_reports.py` invoked by `.github/workflows/weather.yaml`.
- `scheduler.py` appears unwired and inconsistent with the current weather/database interfaces; verify it before using or modifying it as an operational path.
- Keep credentials in environment variables or GitHub Actions secrets. Do not put secret values in documentation.
- See [architecture.md](architecture.md) for verified component and data-flow details.

## Outstanding tasks and known issues

- No outstanding work items are recorded in repository documentation.
- `scheduler.py` has API/import mismatches with the current implementation and is not the workflow's scheduled entry point.

## Relevant files for ongoing work

- [`main.py`](../main.py), [`database.py`](../database.py), [`weather.py`](../weather.py), [`telegram.py`](../telegram.py)
- [`send_reports.py`](../send_reports.py), [`.github/workflows/weather.yaml`](../.github/workflows/weather.yaml)
