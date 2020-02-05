from typing import Optional

from .models import TrainOrder

from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import bold, text


def successful_ticket_order(train_order: TrainOrder) -> str:
    msg = text(text('Ticket order was successful! :tada: :tada:'),
               text(bold('Information:'), train_order), sep='\n')
    return emojize(msg)


def failed_ticket_order(train_order: TrainOrder,
                        err_msg: Exception,
                        append: Optional[str] = None) -> str:
    msg = [text(':bomb: Ticker order received an error: ', str(err_msg)),
           text(bold('Information:'), train_order)]
    if append:
        msg.append(text(bold('Additional info:'), append))
    return emojize(text(*msg))


def failed_on_captcha(train_order: TrainOrder):
    msg = text(':warning: Blocked on captcha :warning:',
               text(bold('Information:'), train_order))
    return emojize(msg)


def updated_captcha_session(train_order: TrainOrder):
    msg = text(':ok: Updated captcha, everything is fine :ok',
               text(bold('Information:', train_order)), sep='\n')
    return emojize(msg)
