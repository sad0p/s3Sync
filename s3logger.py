import logging


def create_logger(log_path=None):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if log_path is None:
        fh_logger = logging.StreamHandler()
    else:
        fh_logger = logging.FileHandler(log_path)

    logger_formatter = logging.Formatter(
        '%(levelname)s:%(asctime)s:%(funcName)s:%(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
    fh_logger.setFormatter(logger_formatter)
    logger.addHandler(fh_logger)
    return logger
