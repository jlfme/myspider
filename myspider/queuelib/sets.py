#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-03-13 21:25:18
# ---------------------------------------


from myspider.queuelib.connection import get_connection_from_settings
from myspider.queuelib.serializers import PickleSerializer


class RedisSet(object):
    def __init__(self, key, connection=None, serializer=None):
        self.key = key
        self.connection = connection or get_connection_from_settings()
        self.serializer = serializer if serializer is not None else PickleSerializer()

    def add(self, value):
        self.connection.sadd(self.key, self.serializer.dumps(value))

    def pop(self):
        """随机移除一个元素并返回"""
        data = self.connection.spop(self.key)
        if data:
            return self.serializer.loads(data)
        else:
            return None

    def ismember(self, key):
        """是否存在指定key"""
        return self.connection.sismember(self.key, self.serializer.dumps(key))

    def get(self):
        """随机返回集合中的一个元素"""
        data = self.connection.srandmember(self.key)
        if data:
            return self.serializer.loads(data)
        else:
            return None

    def update(self, s):
        if not isinstance(s, set):
            raise TypeError("'{s}' must be a set")
        for i in s:
            self.add(s)

    def remove(self, key):
        self.connection.srem(self.key, self.serializer.dumps(key))

    def members(self):
        _set = set()
        for item in self.connection.smembers(self.key):
            _set.add(self.serializer.loads(item))
        return _set

    @property
    def size(self):
        return self.connection.scard(self.key)

    def clear(self):
        self.connection.delete(self.key)
