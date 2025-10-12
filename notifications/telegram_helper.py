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
        raise Exception(f"Esception: {response.text}")


def send_telegram_overdue_message(borrowing: Borrowing):

    text = (
        f"Borrowing {borrowing.id} is overdue!\n"
        f"user: {borrowing.user}\n"
        f"borrow date: {borrowing.borrow_date}\n"
        "*NOT RETURNED ON*\n"
        f"*expected return date*: {borrowing.expected_return_date}"
    )
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}

    response = requests.post(url, data=payload)
    if not response.ok:
        raise Exception(f"Exception: {response.text}")
