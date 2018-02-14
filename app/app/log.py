import logging
import inspect
import os
from app import application


def _get_binary_name():
    return os.path.basename(inspect.stack()[-1][1])


def _get_log_file_path(binary=None):
    logfile = application.config.get('LOG_FILE', None)
    logdir = application.config.get('LOG_DIR', None)

    if logfile and not logdir:
        return logfile

    if logfile and logdir:
        return os.path.join(logdir, logfile)

    if logdir:
        binary = binary or _get_binary_name()

        return "{}.log".format(os.path.join(logdir, binary))

    return None


def _get_formatter():
    date_fmt = "%Y-%m-%d %H:%M:%S"
    log_fmt = '%(asctime)s %(levelname)s %(name)s:%(lineno)d %(message)s'

    formatter = logging.Formatter(log_fmt, date_fmt)
    return formatter


def getLogger(name='unknown', version='unknown'):
    log_file = _get_log_file_path()
    formatter = _get_formatter()

    if log_file is None:
        handler = logging.StreamHandler()
    else:
        handler = logging.FileHandler(log_file)

    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.addHandler(handler)
    if application.config.get('DEBUG', False):
        logger.setLevel(logging.DEBUG)
    elif application.config.get('VERBOSE', False):
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    return logger
