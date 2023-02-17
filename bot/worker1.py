#!/usr/bin/env python3
import datetime
import logging
import requests
import os

from db.dbHelper import dbHelper


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

PATH = os.path.dirname(os.path.abspath(__file__))

def send_message(token, chat_id, product):
    
    bot_token = token
    bot_chatID = chat_id
    bot_message = f"Please utilize {product} before tomorrow"
    send_text = (
        "https://api.telegram.org/bot"
        + bot_token
        + "/sendMessage?chat_id="
        + bot_chatID
        + "&parse_mode=Markdown&text="
        + bot_message
    )

    response = requests.get(send_text)

    return response.json()


def get_secret(key, default):
    value = os.getenv(key, default)
    if os.path.isfile(value):
        with open(value) as f:
            return f.read()
    return value

def main():

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    
    TOKEN = get_secret('bot_token','')

    current_date = datetime.datetime.now()
    db = dbHelper("worker")
    result = db.check_notification(current_date)
    if result:
        for nid, chat, is_notified, notif_date, is_freez, link, product in result:
            if is_notified:
                logger.info("user was alredy notified")
            else:
                send_message(TOKEN, chat, product)
                db.update_is_notified(nid)
                logger.info("Notification sent")
    else:
        logger.info("No notifications today")


if __name__ == "__main__":
    main()
