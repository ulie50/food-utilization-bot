#!/usr/bin/env python
#Idee: add calculation of similar word to make a suggestion
import os
import logging
import requests
from db.dbHelper import dbHelper

import telegram
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler
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
        f"Hi {str(user.mention_markdown_v2())}\!",
        #reply_markup=button,
        reply_markup={
            "inline_keyboard": [
                [
                {
                    "text": "🇬🇧 english",
                    "callback_data": "en"
                },
                {
                    "text": "🇩🇪 deutsch",
                    "callback_data": "de"
                },
                {
                    "text": "русский",
                    "callback_data": "ru"
                }
                ]
            ]
            }
 
    )


def command_handler_help(update: Update, _: CallbackContext,language=None):
    db = dbHelper("user")

    if language:
        if update.message:
            update.message.reply_text(db.get_phrase(phrase_id=1,language=language).phrase)
            
        elif update.callback_query.message:
            update.callback_query.message.reply_text(db.get_phrase(phrase_id=1,language=language).phrase)

    else:
        language = db.get_user_language(chat_id=update.effective_message.chat_id)
        if language:
            command_handler_help(update,_,language)
        else:
            update.message.reply_text("Please select language from start menu")


def callback_query_handler(update:Update, _: CallbackContext):
    callback_data = update.callback_query.data
    db = dbHelper("user")
    db.add_chat(chat=update.effective_message.chat_id,language=callback_data)
    command_handler_help( update,_,callback_data)


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

    language = db.get_user_language(chat_id=update.effective_message.chat_id)
    if language:
        product_info = db.is_item_in_db(msg_text.lower(),language)
        if product_info:
            *info,product_id = product_info
            if product_id:
                logger.info(f"{msg_text}is in DB")
                id,days,*rest = db.getDays(product_id)
                notification_id = db.add_notification(chat=str(chat_id), message=msg_text, days=days)
                db.add_entrance(chat=str(chat_id), message=msg_text, inDB=True,notification_id = notification_id)
                reply_text = db.get_phrase(2,language=language)
                update.message.reply_text(reply_text.phrase)
                logger.info(f"set schedule for {msg_text}")

        else:
            logger.info(f"{msg_text}is not DB")

            db.add_entrance(chat=str(chat_id), message=msg_text,inDB=False)
            reply_text = db.get_phrase(3,language=language)
            update.message.reply_text(reply_text.phrase)
            logger.info(f"{msg_text} doesnt exist in DB")
    else:
        update.message.reply_text("Please select language from start menu")


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
    dispatcher.add_handler(CommandHandler("help", command_handler_help))

    # on non command i.e message - echo the message on Telegram
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, writeInDB))
    dispatcher.add_handler(CallbackQueryHandler(callback_query_handler))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()