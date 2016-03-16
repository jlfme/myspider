#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-03-13 21:28:18
# ---------------------------------------


from .connection import get_connection_from_settings
from .serializers import PickleSerializer


class RedisDict(object):
    def __init__(self, key, connection=None, serializer=None):
        self.key = key
        self.connection = connection or get_connection_from_settings()
        self.serializer = serializer if serializer is not None else PickleSerializer()

    def add(self, key, value):
        self.connection.hset(self.key, key, self.serializer.dumps(value))

    def has_key(self, key):
        return self.connection.hexists(self.key, key)

    def get(self, key, default=None):
        """是否存在指定key, 有就返回对应的值"""
        data = self.connection.hget(self.key, key)
        if data:
            return self.serializer.loads(data)
        return default or None

    def members(self):
        """返回所有元素"""
        return self.connection.hgetall(self.key)

    @property
    def size(self):
        return self.connection.hlen(self.key)

    @property
    def name(self):
        return self.key

    def clear(self):
        self.connection.delete(self.key)
