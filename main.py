from fastapi import FastAPI, Request
from telegram import answer_callback_query, send_message
from database import get_user, initialize_database, subscribe_user, unsubscribe_user, set_report_time
from datetime import datetime

from weather import format_current_weather, get_weather

initialize_database()
app = FastAPI()

def show_main_menu(chat_id):

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "🌤️ Today's Weather",
                    "callback_data": "weather"
                }
            ],
            [
                {
                    "text": "⏰ Set Report Time",
                    "callback_data": "set_time"
                }
            ]
        ]
    }

    send_message(
        chat_id,
        "🌤️ Weather Bot\n\nWhat would you like to do?",
        keyboard
    )

def show_time_menu(chat_id):

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "06:00",
                    "callback_data": "time:06:00"
                },
                {
                    "text": "07:00",
                    "callback_data": "time:07:00"
                }
            ],
            [
                {
                    "text": "08:00",
                    "callback_data": "time:08:00"
                },
                {
                    "text": "09:00",
                    "callback_data": "time:09:00"
                }
            ],
            [
                {
                    "text": "10:00",
                    "callback_data": "time:10:00"
                },
                {
                    "text": "✏️ Custom",
                    "callback_data": "time:custom"
                }
            ],
            [
                {
                    "text": "⬅️ Back",
                    "callback_data": "main_menu"
                }
            ]
        ]
    }

    send_message(
        chat_id,
        "⏰ Daily Report Time\n\n"
        "When should I send your weather report?",
        keyboard
    )

@app.get("/")
def home():
    return {"status": "ok"}

def valid_time(value):

    try:
        datetime.strptime(value, "%H:%M")
        return True

    except ValueError:
        return False

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):

    update = await request.json()

    print(update)

    if "message" in update:

        message = update["message"]

        chat_id = message["chat"]["id"]

        text = message.get("text", "")

        # Handle normal messages here
        if text == "/start":

            subscribe_user(chat_id)

            show_main_menu(chat_id)

        elif text == "/stop":

            unsubscribe_user(chat_id)

            send_message(
                chat_id,
                "🔕 You have been unsubscribed."
            )


    elif "callback_query" in update:

        callback = update["callback_query"]

        callback_id = callback["id"]

        data = callback["data"]

        chat_id = callback["message"]["chat"]["id"]

        answer_callback_query(callback_id)

        if data == "weather":

            try:

                user = get_user(chat_id)

                if user is None:
                    send_message(
                        chat_id,
                        "❌ I couldn't find your settings."
                    )
                    return {"ok": True}

                weather = get_weather(
                    user["latitude"],
                    user["longitude"]
                )

                report = format_current_weather(weather)

                send_message(
                    chat_id,
                    report
                )

            except Exception as e:

                print(f"Weather error: {e}")

                send_message(
                    chat_id,
                    "❌ Sorry, I couldn't retrieve the weather right now."
                )

        elif data == "set_time":

            show_time_menu(chat_id)

        elif data.startswith("time:"):

            selected_time = data.removeprefix("time:")

            set_report_time(
                chat_id,
                selected_time
            )

            send_message(
                chat_id,
                f"✅ Daily weather report set to {selected_time}."
            )

        elif data == "time:custom":

            send_message(
                chat_id,
                "✏️ Enter your desired time.\n\n"
                "Example: 07:30"
            )

        elif data == "main_menu":

            show_main_menu(chat_id)
    return {"ok": True}
