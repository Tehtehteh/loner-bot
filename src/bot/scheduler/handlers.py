import os
import logging
import pickle

from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from apscheduler.jobstores.redis import RedisJobStore

from .scheduler import AsyncIOScheduler
from .utils import make_ticket_order_job_id
from ..core import bot
from ..captcha_solver.anti_captcha import AntiCaptchaSolver
from ..models.train_order import TrainOrder
from ..train_service.service import TrainService
from ..train_service.errors import (
    CaptchaRequiredException, InvalidInputDateException,
    SeatAlreadyBookedException, TooManySeatsOrderedException,
    UnknownError, ServerFaultException
)
from ..messages import (
    successful_ticket_order, failed_ticket_order,
    updated_captcha_session
)


scheduler = AsyncIOScheduler()
# Commenting for now
scheduler.add_jobstore(RedisJobStore(db=1, host=os.environ.get('REDIS_HOST', 'redis'),
                                     pickle_protocol=pickle.DEFAULT_PROTOCOL))
logger = logging.getLogger(__name__)


async def poll_ticket_service_task(message: Message,
                                   ticket_order: TrainOrder,
                                   train_service: TrainService,
                                   captcha: Optional[str] = None,
                                   ):
    group_id = f'ticket-booking-{message.from_user.username}-{ticket_order.date}'
    job_id = make_ticket_order_job_id(message.from_user.username,
                                      ticket_order.from_station_id,
                                      ticket_order.to_station_id,
                                      ticket_order.date)
    try:
        response = await train_service.make_order(ticket_order, captcha=captcha)
        logger.info("Got response from Train Service: %s", response)
        msg = successful_ticket_order(ticket_order)
        await bot.send_message(message.chat.id, msg, parse_mode=types.ParseMode.MARKDOWN)
    except SeatAlreadyBookedException as err:
        # don't stop polling, because we might catch it up a little bit later
        msg = failed_ticket_order(ticket_order, err)
        await bot.send_message(message.chat.id, msg, parse_mode=types.ParseMode.MARKDOWN)
    except ServerFaultException as err:
        # retry immediately
        logger.error("Server fault encountered: %s, retrying request immediately.", err)
        scheduler.retry_immediately(job_id)
    except (InvalidInputDateException, UnknownError) as err:
        # stop polling because date is invalid already
        logger.info('Stopping polling, because ticker order date is invalid. Job id: %s', job_id)
        scheduler.remove_job(job_id=job_id)
        additional_info = "Дата указана некорректно или неизвестная ошибка." \
                          " Останавливаем автоматическое бронирование."
        msg = failed_ticket_order(ticket_order, err, additional_info)
        await bot.send_message(message.chat.id, msg, parse_mode=types.ParseMode.MARKDOWN)
    except (CaptchaRequiredException, TooManySeatsOrderedException) as e:
        captcha_fn = await train_service.renew_captcha(renew_gv_session_id=isinstance(e, TooManySeatsOrderedException))
        captcha_solver = AntiCaptchaSolver(client_key=os.environ.get('AC_CLIENT_KEY'))
        scheduler.pause_jobs_by_group(group_id)
        solved = await captcha_solver.solve_from_file(captcha_fn)
        msg = updated_captcha_session(ticket_order)
        await bot.send_message(message.chat.id, msg, parse_mode=types.ParseMode.MARKDOWN)
        scheduler.reschedule_group(group_id, captcha=solved)
