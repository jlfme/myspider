#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-03-13 21:48:18
# ---------------------------------------


import queue as Queue
from .connection import get_connection_from_settings
from .serializers import PickleSerializer


class BaseQueue(object):
    """Per-spider base queue class"""

    Empty = Queue.Empty
    Full = Queue.Full

    def __init__(self, key, connection=None, serializer=None):
        self.key = key
        self.connection = connection or get_connection_from_settings()
        self.serializer = serializer if serializer is not None else PickleSerializer()

    def __len__(self):
        """Return the length of the queue"""
        raise NotImplementedError

    def put(self, request):
        """Push a request"""
        raise NotImplementedError

    def get(self, timeout=0):
        """Pop a request"""
        raise NotImplementedError

    def clear(self):
        self.connection.delete(self.key)

    def qsize(self):
        return self.connection.llen(self.key)


class FifoQueue(BaseQueue):
    """Per-spider FIFO queue"""

    def __len__(self):
        return self.qsize()

    def put(self, request):
        """Push a request"""
        self.connection.lpush(self.key, self.serializer.dumps(request))

    def get(self, timeout=0):
        """Pop a request"""
        if timeout > 0:
            data = self.connection.brpop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = self.connection.rpop(self.key)
        if data:
            return self.serializer.loads(data)


class LifoQueue(BaseQueue):
    """LIFO queue"""

    def __len__(self):
        return self.qsize()

    def put(self, request):
        """Push a request"""
        self.connection.lpush(self.key, self.serializer.dumps(request))

    def get(self, timeout=0):
        """Pop a request"""
        if timeout > 0:
            data = self.connection.brpop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = self.connection.lpop(self.key)
        if data:
            return self.serializer.loads(data)
