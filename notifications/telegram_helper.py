import os
import requests

from dotenv import load_dotenv

from borrowings.models import Borrowing
from payments.models import Payment

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


def send_message(message: str):
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, data=payload)
    if not response.ok:
        raise Exception(f"Exception: {response.text}")


def send_telegram_message(message: str):
    send_message(message)


def send_telegram_overdue_message(borrowing: Borrowing):

    message = (
        f"📚📚📚 *OVERDUE BORROWING ALERT!* 📚📚📚\n\n"
        f"📖 *Borrowing ID:* {borrowing.id}\n"
        f"👤 *User:* {borrowing.user}\n"
        f"📅 *Borrow date:* {borrowing.borrow_date}\n"
        f"⚠️ *Not returned on time!*\n"
        f"⏰ *Expected return date:* {borrowing.expected_return_date}\n\n"
        f"📚📚📚 Please remind the user to return their book 📚📚📚"
    )
    send_message(message)


def send_successfull_payment_notification(payment: Payment):
    message = f"✅ Payment #{payment.id} completed.\nAmount: {payment.amount}"
    send_message(message)
