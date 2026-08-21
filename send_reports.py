from datetime import datetime
from zoneinfo import ZoneInfo

from database import get_subscribed_users, mark_report_sent
from weather import format_current_weather, get_weather
from telegram import send_message


def is_report_due(user):

    timezone = user["timezone"]
    report_time = user["report_time"]
    last_sent_date = user["last_sent_date"]

    now = datetime.now(ZoneInfo(timezone))

    current_time = now.strftime("%H:%M")
    today = now.strftime("%Y-%m-%d")

    # Already sent today
    if last_sent_date == today:
        return False

    # Not time yet
    if current_time < report_time:
        return False

    return True

def process_user(user):

    if not is_report_due(user):
        return

    print(
        f"Sending report to {user['telegram_id']}"
    )

    weather = get_weather(
        user["latitude"],
        user["longitude"]
    )

    report = format_current_weather(weather)

    send_message(
        user["telegram_id"],
        report
    )

    today = datetime.now(
        ZoneInfo(user["timezone"])
    ).strftime("%Y-%m-%d")

    mark_report_sent(
        user["telegram_id"],
        today
    )


def main():

    users = get_subscribed_users()

    print(f"Checking {len(users)} users...")

    for user in users:

        try:
            process_user(user)

        except Exception as e:

            print(
                f"Failed to process "
                f"{user['telegram_id']}: {e}"
            )


if __name__ == "__main__":
    main()