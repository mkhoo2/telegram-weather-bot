import os
import requests

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def answer_callback_query(callback_query_id):

    url = f"{BASE_URL}/answerCallbackQuery"

    data = {
        "callback_query_id": callback_query_id
    }

    response = requests.post(
        url,
        json=data,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def send_message(chat_id, text, reply_markup=None):

    url = f"{BASE_URL}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        data["reply_markup"] = reply_markup

    response = requests.post(
        url,
        json=data,
        timeout=10
    )

    response.raise_for_status()

    return response.json()