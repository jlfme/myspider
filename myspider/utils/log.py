#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-01-25 20:47:18
# ---------------------------------------


import logging


class Logger(object):

    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    @staticmethod
    def get_logger(name, log_level=None, log_type=None):

        logger = logging.getLogger(name)

        # 日志级别
        """
        级别高低顺序：NOTSET < DEBUG < INFO < WARNING < ERROR < CRITICAL
        """
        if log_level:
            logger.setLevel(log_level)
        else:
            logger.setLevel(logging.DEBUG)

        # 日志格式设置
        formatter = logging.Formatter('[%(asctime)s] %(name)s [%(levelname)s]   %(message)s')

        if log_type == 'console':
            # 控制台日志
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        elif log_type == 'file':
            # 文件日志
            fh = logging.FileHandler('log.txt', 'w')
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        else:
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            logger.addHandler(ch)

            fh = logging.FileHandler('log.txt', 'w')
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        return logger
