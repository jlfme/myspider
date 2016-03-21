#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-03-21 23:30:18
# ---------------------------------------


import logging
from .escape import escape_codes, parse_colors


default_log_colors = {
    'DEBUG': 'purple',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red',
}


default_formatter_dict = {
    '%': '%(log_color)s %(asctime)s %(levelname)s %(name)s %(message)s',
    '{': '{log_color}[{asctime}] {levelname} {name} {message}'
}


class ColoredRecord(object):
    """
    Wraps a LogRecord, adding named escape codes to the internal dict.
    The internal dict is used when formatting the message (by the PercentStyle,
    StrFormatStyle, and StringTemplateStyle classes).
    """

    def __init__(self, record):
        """Add attributes from the escape_codes dict and the record.

        :param record:
        """
        self.__dict__.update(escape_codes)
        self.__dict__.update(record.__dict__)

        # Keep a reference to the original record so ``__getattr__`` can
        # access functions that are not in ``__dict__``
        self.__record = record

    def __getattr__(self, name):
        return getattr(self.__record, name)


class ColoredFormatter(logging.Formatter):
    """
    A formatter that allows colors to be placed in the format string.
    Intended to help in creating more readable logging output.
    """

    def __init__(self, fmt=None, datefmt=None, style='%',
                 log_colors=None, reset=True):

        fmt = fmt or default_formatter_dict[style]

        super(ColoredFormatter, self).__init__(fmt, datefmt, style)
        self.log_colors = log_colors or default_log_colors
        self.reset = reset

    @staticmethod
    def color(log_colors, level_name):
        """Return escape codes from a ``log_colors`` dict."""
        return parse_colors(log_colors.get(level_name, ""))

    def format(self, record):
        """Format a message from a record object."""
        record = ColoredRecord(record)
        record.log_color = self.color(self.log_colors, record.levelname)

        # Format the message
        message = super(ColoredFormatter, self).format(record)

        # Add a reset code to the end of the message
        # (if it wasn't explicitly added in format str)
        if self.reset and not message.endswith(escape_codes['reset']):
            message += escape_codes['reset']

        return message
