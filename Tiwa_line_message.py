import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_TOKEN")
RECIPIENT_ID = os.getenv("LINE_USER_ID_TOKEN")


def send_line_message(to, message):
    url = "https://api.line.me/v2/bot/message/push"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }

    data = {"to": to, "messages": [{"type": "text", "text": message}]}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx

        if response.status_code == 200:
            print("Message sent successfully!")
        else:
            print(f"Failed to send message: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


# Replace with your recipient ID and message
recipient_id = RECIPIENT_ID
message_text = "Hello, this is a test"

send_line_message(recipient_id, message_text)
