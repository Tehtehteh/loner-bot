from aiogram.dispatcher.filters.state import State, StatesGroup


class TicketOrderState(StatesGroup):
    from_station_input = State()
    from_station_get = State()
    to_station_input = State()
    to_station_get = State()
    date = State()
    train_code = State()
    wagon_type = State()
    wagon_number = State()
    seats = State()
    is_ok = State()


class CaptchaRenewState(StatesGroup):
    captcha_verified = State()
