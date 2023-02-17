#!/usr/bin/env python

import os
import logging
import requests
from db.dbHelper import dbHelper

from telegram import Update, ForceReply
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)
PATH = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        f"Hi {user.mention_markdown_v2()}!",
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


def echo(update: Update, _: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def set_scheduled_msg(token, chat_id, bot_message, schedule_date):

    bot_token = token
    bot_chatID = chat_id
    send_text = (
        "https://api.telegram.org/bot"
        + bot_token
        + "/sendMessage?chat_id="
        + bot_chatID
        + "&parse_mode=Markdown&text="
        + bot_message
        + "&schedule_date="
        + schedule_date
    )

    response = requests.get(send_text)

    return response.json()


def writeInDB(update: Update, _: CallbackContext) -> None:
    """writes users's message into the DB"""
    msg_upd = update.message
    msg_text = msg_upd.text
    chat_id = update.effective_message.chat_id
    db = dbHelper("user")

    product = db.is_item_in_db(msg_text.lower())
    if product:
        logger.info(f"{msg_text}is in DB")
        days = db.getDays(product[1])
        db.add2notification(chat=str(chat_id), message=msg_text, days=days)
        db.add2entrance(chat=str(chat_id), message=msg_text, inDB=True)
        update.message.reply_text("Ok, got it!")
        logger.info(f"set schedule for {msg_text}")

    else:
        logger.info(f"{msg_text}is not DB")

        db.add2entrance(chat=str(chat_id), message=msg_text, inDB=False)
        update.message.reply_text("Uh, sorry we do not have info about this product")
        logger.info(f"{msg_text} doesnt exist in DB")

def get_secret(key, default):
    value = os.getenv(key, default)
    if os.path.isfile(value):
        with open(value) as f:
            return f.read()
    return value

def main() -> None:

    TOKEN = get_secret('bot_token','')
  
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, writeInDB))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()