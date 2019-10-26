import logging


DEFAULT_FORMATTER = logging.Formatter('%(levelname)s: [%(asctime)s][%(filename)s:%(lineno)d]: %(message)s')


def setup_logging(debug: bool = False):
    app_logger = logging.getLogger('bot')
    stdout_handler = logging.StreamHandler()
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        stdout_handler.setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger('apscheduler.scheduler').setLevel(logging.INFO)
        stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(DEFAULT_FORMATTER)
    app_logger.addHandler(stdout_handler)
    train_service_logger = logging.getLogger('train_service')
    train_service_logger.addHandler(stdout_handler)

