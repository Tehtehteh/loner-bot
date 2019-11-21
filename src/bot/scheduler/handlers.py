# import os
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.jobstores.redis import RedisJobStore

from ..train_service.service import TrainService
from ..train_service.errors import (
    CaptchaRequiredException, InvalidInputDateException,
    SeatAlreadyBookedException, TooManySeatsOrderedException,
    UnknownError
)
from .utils import make_ticket_order_job_id

scheduler = AsyncIOScheduler()
# Commenting for now
# scheduler.add_jobstore(RedisJobStore(db=1, host=os.environ.get('REDIS_HOST', 'redis')))
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
    except (InvalidInputDateException, UnknownError):
        # stop polling because date is invalid already
        job_id = make_ticket_order_job_id(message.from_user.username,
                                          ticket_order.from_station_id,
                                          ticket_order.to_station_id,
                                          ticket_order.date)
        logger.info('Stopping polling, because ticker order date is invalid. Job id: %s', job_id)
        scheduler.remove_job(job_id=job_id)
        msg = "Дата указана некорректно или неизвестная ошибка. Останавливаем автоматическое бронирование."
        await bot.send_message(message.chat.id, msg)
    except CaptchaRequiredException:
        captcha_fn = await train_service.renew_captcha()
        with open(captcha_fn, 'rb') as captcha_fd:
            await bot.send_photo(message.chat.id, captcha_fd,
                                 caption='УЗ требует ввода капчи. Введите, пожалуйста цифры на картинке.')
    except TooManySeatsOrderedException:
        logger.info('Renewing session, because of TooManySeatsOrderedException')
        captcha_fn = await train_service.renew_captcha(renew_gv_session_id=True)
        with open(captcha_fn, 'rb') as captcha_fd:
            await bot.send_photo(message.chat.id, captcha_fd,
                                 caption='Сессия была обновлена и УЗ требует ввода капчи. '
                                         'Введите, пожалуйста цифры на картинке.')

