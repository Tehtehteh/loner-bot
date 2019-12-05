import os
import enum
import base64
import asyncio
import logging

import aiohttp

from typing import Any, Optional

from .interface import ICaptchaSolver


logger = logging.getLogger('anti-captcha')


class TaskType(enum.Enum):
    IMAGE_TO_TEXT_TASK = 'ImageToTextTask'


class AntiCaptchaAPIError(Exception):
    def __init__(self, error_code: str,
                 error_description: str):
        self.error_code = error_code
        self.error_description = error_description

    def __str__(self):
        return f'Error from anti-captcha service. Code: {self.error_code}, description: {self.error_description}'


class AntiCaptchaSolver(ICaptchaSolver):

    ANTI_CAPTCHA_API_URL = 'https://api.anti-captcha.com'
    CREATE_TASK_ENDPOINT = 'createTask'
    GET_TASK_ENDPOINT = 'getTaskResult'
    _headers = {'Content-Type': 'application/json'}

    def __init__(self, client_key: str):
        self.client_key = client_key

    async def solve_from_file(self, file_name: str) -> str:
        if not os.path.exists(file_name):
            raise FileNotFoundError(f'{file_name} does not exists')
        with open(file_name, mode='rb') as file_handler:
            buffer = file_handler.read()
            data = base64.b64encode(buffer)
            body = self._create_request_body(data)
            try:
                async with aiohttp.request('POST',
                                       f'{self.ANTI_CAPTCHA_API_URL}/{self.CREATE_TASK_ENDPOINT}',
                                       json=body, headers=self._headers) as response:

                    response = await response.json()
                    task_id = self._parse_response(response)
                    while True:
                        solution = await self._check_task_status(task_id)
                        if solution:
                            return solution
                        await asyncio.sleep(1)
            except Exception as e:
                logger.exception('Got exception running anti-captcha: %s. Retrying...', e, exc_info=True)
                await self.solve_from_file(file_name)

    async def _check_task_status(self, task_id: int) -> Optional[str]:
        url = f'{self.ANTI_CAPTCHA_API_URL}/{self.GET_TASK_ENDPOINT}'
        body = {
            'clientKey': self.client_key,
            'taskId': task_id
        }
        async with aiohttp.request('POST', url, json=body) as response:
            response = await response.json()
            self._check_error(response)
            status = response['status']
            if status == 'ready':
                return response['solution']['text']
            return None

    @staticmethod
    def _check_error(response) -> None:
        if response['errorId'] != 0:
            raise AntiCaptchaAPIError(error_code=response['errorCode'],
                                      error_description=response['errorDescription'])

    def _parse_response(self, response: dict) -> int:
        self._check_error(response)
        task_id = response['taskId']
        return task_id

    def _create_request_body(self,
                             data: bytes,
                             task_type: TaskType = TaskType.IMAGE_TO_TEXT_TASK,
                             numeric: bool = True) -> dict:
        payload = {
            'clientKey': self.client_key,
            'task': {
                'type': task_type.value,
                'body': data.decode(encoding='utf-8'),
                'phrase': False,
                'numeric': numeric,
                'math': 0,
                'minLenght': 4,  # because we are pretty sure about UZ captcha
                'maxLength': 4   # because we are pretty sure about UZ captcha
            }
        }
        return payload

    async def solve_from_url(self, url: str) -> str:
        pass