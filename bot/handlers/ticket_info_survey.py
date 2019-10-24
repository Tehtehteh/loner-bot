import logging

from datetime import datetime, timedelta

import aiogram.utils.markdown as md

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from .state import TicketOrderState
from ..train_service.service import TrainService
from ..models.train_order import TrainOrder, WagonType
from ..scheduler.handlers import scheduler, poll_ticket_service_task

logger = logging.getLogger(__name__)


async def start_ticket_info_survey(message: types.Message):
    logger.info('User %s started ticket info survey.', message.from_user.username)
    await TicketOrderState.from_station_input.set()
    await message.reply("Напиши станцию отправления. Пример: Надворная.")


def get_departure_station(dp: Dispatcher):
    async def _get_departure_station(message: types.Message, state: FSMContext):
        search_term = message.text
        stations = await TrainService().stations_search(search_term)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        for station in stations:
            markup.add(f'{station["title"]}({station["value"]})')
        await TicketOrderState.next()
        await message.reply("Выберите станцию из списка ниже.", reply_markup=markup)

    dp.register_message_handler(_get_departure_station, state=TicketOrderState.from_station_input)


def get_departure_station_input(dp: Dispatcher):
    async def _get_departure_station_input(message: types.Message, state: FSMContext):
        text = message.text
        async with state.proxy() as data:
            departure_station_id = text[text.index('(') + 1:text.index(')')]
            data['from_station'] = departure_station_id
            logger.info('User %s has chosen %s departure station id.', message.from_user.username,
                        departure_station_id)
        await TicketOrderState.next()
        await message.reply("Введите название станции прибытия. Пример: Львов.",
                            reply_markup=types.ReplyKeyboardRemove())

    dp.register_message_handler(_get_departure_station_input,
                                state=TicketOrderState.from_station_get)


def get_arrival_station(dp: Dispatcher):
    async def _get_arrival_station(message: types.Message, state: FSMContext):
        logger.info('User %s has set arrival station: %s', message.from_user.username,
                    message.text)
        search_term = message.text
        stations = await TrainService().stations_search(search_term)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        for station in stations:
            markup.add(f'{station["title"]}({station["value"]})')
        await TicketOrderState.next()
        await message.reply("Выберите станцию из списка ниже.",
                            reply_markup=markup)

    dp.register_message_handler(_get_arrival_station, state=TicketOrderState.to_station_input)


def get_arrival_station_input(dp: Dispatcher):
    async def _get_arrival_station_input(message: types.Message, state: FSMContext):
        logger.info('User %s has set arrival station: %s', message.from_user.username,
                    message.text)
        text = message.text
        async with state.proxy() as data:
            departure_station_id = text[text.index('(') + 1:text.index(')')]
            data['to_station'] = departure_station_id
            logger.info('User %s has chosen %s arrival station id.', message.from_user.username,
                        departure_station_id)
        await TicketOrderState.next()
        await message.reply("Введите дату отправления в формате %Y-%m-%d. Пример: 2019-11-16",
                            reply_markup=types.ReplyKeyboardRemove())

    dp.register_message_handler(_get_arrival_station_input, state=TicketOrderState.to_station_get)


def get_date(dp: Dispatcher):
    async def _get_date(message: types.Message, state: FSMContext):
        logger.info('User %s has set departure date: %s', message.from_user.username,
                    message.text)
        async with state.proxy() as data:
            data['date'] = message.text
            logger.info('Current state: %s', data)
        await TicketOrderState.next()
        await message.reply("Введите номер вагона.")

    dp.register_message_handler(_get_date, state=TicketOrderState.date)


def get_train_code(dp: Dispatcher):
    async def _get_date(message: types.Message, state: FSMContext):
        logger.info('User %s has set departure date: %s', message.from_user.username,
                    message.text)
        async with state.proxy() as data:
            data['train_code'] = message.text
            logger.info('Current state: %s', data)
        await TicketOrderState.next()
        await message.reply("Введите номер вагона.")

    dp.register_message_handler(_get_date, state=TicketOrderState.train_code)


def get_wagon_type(dp: Dispatcher):
    async def _get_wagon_number(message: types.Message, state: FSMContext):
        logger.info('User %s has set wagon number: %s', message.from_user.username,
                    message.text)
        async with state.proxy() as data:
            data['wagon_type'] = message.text
            logger.info('Current state: %s', data)
        await TicketOrderState.next()
        await message.reply("Введите через запятую номера сидений, которые надо бронировать. Пример: 1,2,3")

    dp.register_message_handler(_get_wagon_number, state=TicketOrderState.wagon_type)


def get_wagon_number(dp: Dispatcher):
    async def _get_wagon_number(message: types.Message, state: FSMContext):
        logger.info('User %s has set wagon number: %s', message.from_user.username,
                    message.text)
        async with state.proxy() as data:
            data['wagon_number'] = message.text
            logger.info('Current state: %s', data)
        await TicketOrderState.next()
        await message.reply("Введите через запятую номера сидений, которые надо бронировать. Пример: 1,2,3")

    dp.register_message_handler(_get_wagon_number, state=TicketOrderState.wagon_number)


def get_seats_number(dp: Dispatcher):
    async def _get_seats_number(message: types.Message, state: FSMContext):
        logger.info('User %s has set seats: %s', message.from_user.username,
                    message.text)
        async with state.proxy() as data:
            seats = message.text.split(',')
            data['seats'] = seats
            logger.info('Current state: %s', data)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("OK", "CANCEL")
        await TicketOrderState.next()
        msg = md.text(
            md.text('Всё правильно?'),
            md.text(md.italic('Станция отправления: '), md.code(data['from_station'])),
            md.text(md.italic('Станция прибытия: '), md.code(data['to_station'])),
            md.text(md.italic('Дата отправления: '), md.code(data['date'])),
            md.text(md.italic('Номер вагона: '), md.code(data['wagon_number'])),
            md.text(md.italic('Бронируемые места: '), md.code(','.join(data['seats']))),
            sep='\n'
        )
        await message.reply(msg, reply_markup=markup, parse_mode=types.ParseMode.MARKDOWN)

    dp.register_message_handler(_get_seats_number, state=TicketOrderState.seats)


def get_final_confirmation(dp: Dispatcher):
    def _filter_ok_response(message: types.Message):
        return message.text == 'OK'

    def _filter_cancel_response(message: types.Message):
        return message.text == 'CANCEL'

    async def _cancel_order_from_confirmation(message: types.Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is None:
            return

        await state.finish()
        await message.reply('Бронирование отменено. Заходьте ще.',
                            reply_markup=types.ReplyKeyboardRemove())

    async def _get_final_confirmation(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            ticket_order = TrainOrder(
                order_number=0,
                from_station_id=2208001,
                to_station_id=2218000,
                train_code='012Ш',
                date='2019-11-16',
                wagon_number=2,
                wagon_class='Б',
                wagon_type=WagonType.K,
                wagon_railway=35,
                charline='Б',
                bedding=1,
                services='М',
                seat_number='008',
                reserve=0
            )
            job_id = f'ticket-booking-{message.from_user.username}-{ticket_order.from_station_id}-{ticket_order.to_station_id}-{ticket_order.date}'
            scheduler.add_job(poll_ticket_service_task, 'interval',
                              args=(message.bot, message, ticket_order, dp),
                              seconds=20 * 60, next_run_time=datetime.now() + timedelta(seconds=3),
                              id=job_id)
        await message.reply('OK! Стартую бронирование лол..', reply_markup=types.ReplyKeyboardRemove())
        await state.finish()

    dp.register_message_handler(_get_final_confirmation,
                                _filter_ok_response,
                                state=TicketOrderState.is_ok)
    dp.register_message_handler(_cancel_order_from_confirmation,
                                _filter_cancel_response,
                                state=TicketOrderState.is_ok)


async def cancel_order_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('Бронирование отменено.', reply_markup=types.ReplyKeyboardRemove())


def get_and_renew_captcha(dp: Dispatcher):

    def _filter_captcha_message(message: types.Message):
        return len(message.text) == 4 and all(x.isdigit() for x in message.text)

    async def _get_and_renew_captcha(message: types.Message):
        captcha_code = message.text
        jobs = scheduler.get_jobs()
        for job in jobs:
            job.modify(kwargs={'captcha': captcha_code}, next_run_time=datetime.now() + timedelta(seconds=3))
        await message.reply('Hehe, thanks for captcha bro...')

    dp.register_message_handler(_get_and_renew_captcha, _filter_captcha_message)
