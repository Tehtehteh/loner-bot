import os
import random

from urllib.parse import quote
from typing import List, Optional
from dataclasses import dataclass, field
from enum import Enum

from jinja2 import Template

SEAT_NUMBER_MAX_LENGTH = 3

# ascii characters are prohibited :D
ru_alphabet_lower = 'абвгдеёжзиклмопрстуфхцчшщэюя'
names = ['Сергій', 'Іван', 'Микола', 'Софія', 'Дмитро', 'Ганна', 'Надія', 'Віктор', 'Василь']
surnames = ['Іванов', 'Морозов', 'Третяк', 'Проценко', 'Сорокін', 'Дубілет', 'Зеленський']


class WagonType(Enum):
    K = 'К'  # Купе
    P = 'П'  # Плацкарт
    L = 'Л'  # Люкс

    def __str__(self):
        return self.value


@dataclass
class Seat:
    number: str
    first_name: str
    last_name: str

    def __post_init__(self):
        if 3 < len(self.number) < 3:
            self._normalize_seat_number()

    def _normalize_seat_number(self):
        self.number = self.number.zfill(SEAT_NUMBER_MAX_LENGTH)


@dataclass
class TrainOrder:
    from_station_id: int
    to_station_id: int
    train_code: str
    date: str
    wagon_number: int
    wagon_class: str
    wagon_type: WagonType
    wagon_railway: int
    seats: List[Seat] = field(default_factory=list)

    @staticmethod
    def roll_random_name(name_list: List[str]) -> str:
        return random.choice(name_list)

    def add_seat(self, seat_number: str,
                 first_name: Optional[str] = None,
                 last_name: Optional[str] = None):
        if not first_name:
            first_name = self.roll_random_name(names)
        if not last_name:
            last_name = self.roll_random_name(surnames)
        seat = Seat(seat_number, first_name, last_name)
        self.seats.append(seat)
        return self

    def serialize(self) -> str:
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               'order_template.jinja2')) as fd:
            tpl = Template(fd.read())
            tpl_str = tpl.render(**vars(self))
            tpl_str = (
                quote(tpl_str.replace('\n', ''))
                    .replace('%3D', '=')
                    .replace('%26', '&')
                    .replace('%20', '')
            )
            return tpl_str
