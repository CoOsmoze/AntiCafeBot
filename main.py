import logging

from telegram.ext import Updater
from telegram import Bot

from command_handler import command_handler
from config import *



def main():
    bot = Bot(token=TOKEN)
    bot.delete_my_commands()

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)

    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    command_handler(dispatcher)
    
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()