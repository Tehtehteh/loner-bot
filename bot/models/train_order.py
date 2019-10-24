import random

from urllib.parse import quote

from dataclasses import dataclass
from enum import Enum


# ascii characters are prohibited :D
ru_alphabet_lower = 'абвгдеёжзиклмопрстуфхцчшщэюя'


class WagonType(Enum):
    K = 'К'  # Купе
    P = 'П'  # Плацкарт
    L = 'Л'  # Люкс

    def __str__(self):
        return self.value


@dataclass
class TrainOrder:
    order_number: int
    from_station_id: int
    to_station_id: int
    train_code: str
    date: str
    wagon_number: int
    wagon_class: str
    wagon_type: WagonType
    wagon_railway: int
    charline: str
    services: str
    seat_number: str
    child = None
    student = None
    first_name: str = ''
    last_name: str = ''
    reserve: int = 0
    bedding: int = 0

    def __post_init__(self):
        self.first_name = self.roll_random_name()
        self.last_name = self.roll_random_name()

    @staticmethod
    def roll_random_name():
        name_length = random.randint(5, 10)
        return ''.join(random.choice(ru_alphabet_lower) for _ in range(name_length)).title()

    def serialize(self) -> str:
        tpl = f"""places[0][ord]=0&
        places[0][from]={self.from_station_id}&
        places[0][to]={self.to_station_id}&
        places[0][train]={self.train_code}&
        places[0][date]={self.date}&
        places[0][wagon_num]={self.wagon_number}&
        places[0][wagon_class]={self.wagon_class}&
        places[0][wagon_type]={self.wagon_type}&
        places[0][wagon_railway]={self.wagon_railway}&
        places[0][charline]=Б&
        places[0][firstname]=Иван&
        places[0][lastname]=Иванов&
        places[0][bedding]=1&
        places[0][services][]=М&
        places[0][child]=&
        places[0][student]=&
        places[0][reserve]=0&
        places[0][place_num]={self.seat_number}
        """
        # todo: normal escape
        return quote(tpl.replace('\n', '').replace(' ', '')).replace('%3D', '=').replace('%26', '&')
