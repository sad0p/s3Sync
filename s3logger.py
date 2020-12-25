import logging


def create_logger(push_log_path):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    fh_logger = logging.FileHandler(push_log_path)
    logger_formatter = logging.Formatter(
        '%(levelname)s:%(asctime)s:%(funcName)s:%(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
    fh_logger.setFormatter(logger_formatter)
    logger.addHandler(fh_logger)
    return logger
