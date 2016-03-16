#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-03-13 21:08:18
# ---------------------------------------


from myspider.utils.python import load_object
from myspider.queuelib import defaults


SETTINGS_PARAMS_MAP = {
    'REDIS_URL': 'url',
    'REDIS_HOST': 'host',
    'REDIS_PORT': 'port',
    'REDIS_ENCODING': 'encoding',
}


def get_connection_from_settings():
    params = defaults.REDIS_PARAMS.copy()
    params.update({'host': defaults.REDIS_HOST, 'port': defaults.REDIS_PORT})
    return get_connection(**params)


def get_connection(**kwargs):
    redis_cls = load_object(kwargs.pop('redis_cls', defaults.REDIS_CLS))
    url = kwargs.pop('url', None)
    if url:
        return redis_cls.from_url(url, **kwargs)
    return redis_cls(**kwargs)
