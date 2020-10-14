class CaptchaRequiredException(Exception):
    ...


class InvalidRequestPayload(Exception):
    ...


class InvalidInputDateException(Exception):
    ...


class SeatAlreadyBookedException(Exception):
    ...


class TooManySeatsOrderedException(Exception):
    ...


class UnknownError(Exception):
    ...


class TrainAlreadyStarted(Exception):
    ...


class ServerFaultException(Exception):
    ...
