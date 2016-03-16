#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-03-13 21:18:18
# ---------------------------------------


REDIS_CLS = 'redis.StrictRedis'
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

REDIS_PARAMS = {
    'socket_timeout': 30,
    'socket_connect_timeout': 30,
    'retry_on_timeout': True,
    'encoding': 'utf-8',
}
