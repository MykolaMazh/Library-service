import os
import requests
from dotenv import load_dotenv

from borrowings.models import Borrowing

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


def send_telegram_message(text: str):
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}

    response = requests.post(url, data=payload)
    if not response.ok:
        raise Exception(f"Exception: {response.text}")


def send_telegram_overdue_message(borrowing: Borrowing):

    text = (
        f"📚📚📚 *OVERDUE BORROWING ALERT!* 📚📚📚\n\n"
        f"📖 *Borrowing ID:* {borrowing.id}\n"
        f"👤 *User:* {borrowing.user}\n"
        f"📅 *Borrow date:* {borrowing.borrow_date}\n"
        f"⚠️ *Not returned on time!*\n"
        f"⏰ *Expected return date:* {borrowing.expected_return_date}\n\n"
        f"📚📚📚 Please remind the user to return their book 📚📚📚"
    )

    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}

    response = requests.post(url, data=payload)
    if not response.ok:
        raise Exception(f"Exception: {response.text}")
