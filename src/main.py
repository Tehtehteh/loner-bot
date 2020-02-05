import os
import logging

from aiogram import executor

from log import setup_logging
from bot.scheduler.handlers import scheduler
from bot.core import create_bot
from bot.handlers.ticket_info_survey import (
    get_arrival_station, get_date, get_departure_station,
    get_departure_station_input,
    get_seats_number, get_wagon_number, start_ticket_info_survey,
    cancel_order_handler, get_final_confirmation, get_arrival_station_input,
    get_train_code, get_wagon_type, list_all_jobs, cancel_order_by_id
)

logger = logging.getLogger('bot')


def main():
    if not os.environ.get('BOT_TOKEN'):
        exit("ERROR: `BOT TOKEN` env variable is required.")
    setup_logging()
    logger.info('Starting scheduler.')
    scheduler.start()
    logger.info('Creating bot with given token.')
    bot, dispatcher = create_bot(os.environ.get('BOT_TOKEN'))
    logger.info('Registering all message handlers.')
    dispatcher.register_message_handler(start_ticket_info_survey,
                                        commands=['start'])
    dispatcher.register_message_handler(cancel_order_handler,
                                        commands=['cancel'], state='*')
    get_departure_station(dispatcher)
    get_departure_station_input(dispatcher)
    get_arrival_station(dispatcher)
    get_arrival_station_input(dispatcher)
    get_wagon_number(dispatcher)
    get_seats_number(dispatcher)
    get_date(dispatcher)
    get_final_confirmation(dispatcher)
    get_train_code(dispatcher)
    get_wagon_type(dispatcher)
    list_all_jobs(dispatcher)
    cancel_order_by_id(dispatcher)
    logger.info('Started bot polling.')
    executor.start_polling(dispatcher)


if __name__ == '__main__':
    main()
