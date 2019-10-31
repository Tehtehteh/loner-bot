import os
import uuid
import aiohttp
import logging

from functools import lru_cache
from urllib.parse import quote

from typing import List, Dict, Any

from ..models.train_order import TrainOrder

from .errors import (
    TooManySeatsOrderedException, SeatAlreadyBookedException,
    CaptchaRequiredException, InvalidInputDateException,
    InvalidRequestPayload
)


logger = logging.getLogger('train_service')


lru_cached = lru_cache()


INVALID_INPUT_DATE_MSG = 'Введена неверная дата'
SEAT_ALREADY_BOOKED_MSG = 'Выбранное вами место'
TOO_MANY_SEATS_ORDERED_MSG = 'Нельзя выбрать больше'


class TrainService:
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    gv_session_id = 'idtnpc6m5qtmpb1i264ebpff65'
    ticket_order_url = 'https://booking.uz.gov.ua/ru/cart/add/'
    stations_search_url = 'https://booking.uz.gov.ua/ru/train_search/station/'
    captcha_url = 'https://booking.uz.gov.ua/ru/captcha'

    @lru_cached
    async def stations_search(self, term: str) -> List[Dict[str, Any]]:
        logger.info('Searching for station by term: %s', term)

        async with aiohttp.request('GET', '?'.join((self.stations_search_url,
                                                    f'term={quote(term)}')),
                                   headers={'Content-Type': 'application/json'}) as response:
            if response.status == 503:
                logger.error('Failed to make a request for stations lookup, code: 503')
            else:
                response_json = await response.json()
                logger.info('Successfully got %d stations from %s term.', len(response_json),
                            term)
                return response_json

    async def make_order(self, train_order: TrainOrder, captcha: str = None) -> str:
        logger.info('Making order ')
        serialized = train_order.serialize()
        if captcha:
            serialized = f'{serialized}&captcha={captcha}'
        async with aiohttp.request('POST', url=self.ticket_order_url,
                                   headers=self.headers, data=serialized,
                                   cookies={'_gv_sessid': TrainService.gv_session_id}) as response:
            if response.status == 503:
                logger.error('Train service is unavailable (probably invalid request payload).')
                raise InvalidRequestPayload
            response_json = await response.json()
            if 'error' in response_json:
                err = response_json['data']['error']
                if isinstance(err, list) and len(err):
                    if err[0].startswith(SEAT_ALREADY_BOOKED_MSG):
                        raise SeatAlreadyBookedException(err)
                    elif err[0].startswith(TOO_MANY_SEATS_ORDERED_MSG):
                        raise TooManySeatsOrderedException(err)
                elif err == INVALID_INPUT_DATE_MSG:
                    raise InvalidInputDateException
                logger.error('Got error from Train service: %s', err)
                return err
            elif 'captcha' in response_json:
                logger.error('Ticket order blocked on captcha.')
                raise CaptchaRequiredException
            return 'Successfully booked your seats, man!'

    async def renew_captcha(self, renew_gv_session_id: bool = False) -> str:
        logger.info('Trying to renew captcha!')
        cookies = {} if renew_gv_session_id else {'_gv_sessid': TrainService.gv_session_id}
        async with aiohttp.request('GET', self.captcha_url,
                                   cookies=cookies) as response:
            if '_gv_sessid' in response.cookies:
                gv_session_id = response.cookies['_gv_sessid'].value
                if gv_session_id != TrainService.gv_session_id:
                    logger.info('Setting new gv session id for TrainService (%s)', gv_session_id)
                    TrainService.gv_session_id = gv_session_id
            captcha_file_name = os.path.join('captchas', str(uuid.uuid4()) + '.jpg')
            with open(captcha_file_name, 'wb') as captcha_fd:
                async for image_part in response.content.iter_chunked(1048):
                    captcha_fd.write(image_part)
                logger.info('Saved captcha file locally, path: %s', captcha_file_name)
            return captcha_file_name
