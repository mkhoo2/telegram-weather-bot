from apscheduler.schedulers.background import BackgroundScheduler

from database import get_subscribed_users
from weather import get_weather, create_report
from telegram import send_message
from datetime import datetime
from zoneinfo import ZoneInfo

def send_due_reports():

    users = get_subscribed_users()

    for telegram_id, report_time, timezone in users:

        now = datetime.now(
            ZoneInfo(timezone)
        )

        current_time = now.strftime("%H:%M")

        if current_time != report_time:
            continue

        weather = get_weather()

        report = create_report(weather)
        print(report)
        send_message(
            telegram_id,
            report
        )


scheduler = BackgroundScheduler()

scheduler.add_job(
    send_due_reports,
    "interval",
    minutes=1
)

scheduler.start()