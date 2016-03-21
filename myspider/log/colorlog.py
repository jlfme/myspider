#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-03-21 21:55:18
# ---------------------------------------


import logging
from .formatters import ColoredFormatter


LOG_LEVEL_DICT = {
    'notset':   logging.NOTSET,
    'debug':    logging.DEBUG,
    'info':     logging.INFO,
    'warning':  logging.WARNING,
    'error':    logging.ERROR,
    'critical': logging.CRITICAL,
    'warn':     logging.WARNING,
    'fatal':    logging.CRITICAL
}


def get_handler(handler_type='console'):
    formatter = ColoredFormatter('{log_color}[{asctime} {levelname}]{reset} [{name}] {message}', style='{')

    if handler_type == 'console':
        handler = logging.StreamHandler()
    elif handler_type == 'file':
        handler = logging.FileHandler(filename='log.log', encoding='utf-8')
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(formatter)
    return handler


def get_logger(log_name=None, log_level='DEBUG', log_type='console'):
    """
    :param log_name: log name
    :param log_level: (str) NOTSET < DEBUG < INFO < WARNING < ERROR < CRITICAL
    :param log_type: (str) 'console' or 'file'
    :return:

    """
    logger = logging.getLogger(log_name)

    if log_level:
        logger.setLevel(LOG_LEVEL_DICT[log_level.lower()])

    if logger.hasHandlers():
        logger.handlers.clear()
    handler = get_handler(log_type)
    logger.addHandler(handler)
    return logger
