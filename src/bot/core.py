import os
from typing import Tuple

from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage


def create_bot(token: str) -> Tuple[Bot, Dispatcher]:
    bot = Bot(token=token)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    return bot, dp


bot, dispatcher = create_bot(os.environ.get('BOT_TOKEN'))
