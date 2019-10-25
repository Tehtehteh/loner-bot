import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ..train_service.service import (
    TrainService, CaptchaRequiredException, InvalidInputDateException,
    SeatAlreadyBookedException
)

scheduler = AsyncIOScheduler()
logger = logging.getLogger(__name__)


async def poll_ticket_service_task(bot: Bot, message: Message, ticket_order, dp: Dispatcher, captcha = None):
    train_service = TrainService()
    try:
        response = await train_service.make_order(ticket_order, captcha=captcha)
        msg = f'Got this response from ticket order service: {response}'
        await bot.send_message(message.chat.id, msg)
    except SeatAlreadyBookedException as err:
        # don't stop polling, because we might
        await bot.send_message(message.chat.id, 'Выбранное вами место уже занято. Выберите ищо: ' + str(err))
    except InvalidInputDateException:
        # stop polling because date is invalid already
        job_id = f'ticket-booking-{message.from_user.username}-{ticket_order.from_station_id}-{ticket_order.to_station_id}-{ticket_order.date}'
        logger.info('Stopping polling, because ticker order date is invalid. Job id: %s', job_id)
        scheduler.remove_job(job_id=job_id)
        await bot.send_message(message.chat.id, "Дата указана некорректно. Останавливаем автоматическое бронирование.")
    except CaptchaRequiredException:
        captcha_fn = await train_service.renew_captcha()
        with open(captcha_fn, 'rb') as captcha_fd:
            await bot.send_photo(message.chat.id, captcha_fd,
                                 caption='УЗ требует ввода капчи. Введите, пожалуйста цифры на картинке.')

