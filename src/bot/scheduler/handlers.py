import os
import logging
import random

from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.jobstores.redis import RedisJobStore

from ..captcha_solver.anti_captcha import AntiCaptchaSolver
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
    except (CaptchaRequiredException, TooManySeatsOrderedException) as e:
        captcha_fn = await train_service.renew_captcha(renew_gv_session_id=isinstance(e, TooManySeatsOrderedException))
        captcha_solver = AntiCaptchaSolver(client_key=os.environ.get('AC_CLIENT_KEY'))
        jobs = scheduler.get_jobs()
        for job in jobs:
            job.pause()
        solved = await captcha_solver.solve_from_file(captcha_fn)
        jobs = scheduler.get_jobs()
        await bot.send_message(message.chat.id, text='Обновил капчу. Продолжаю букинг билетиков :}.')
        for job in jobs:
            callback_time = random.randint(5, 30)
            job.modify(kwargs={'captcha': solved},
                       next_run_time=datetime.now() + timedelta(seconds=callback_time))
