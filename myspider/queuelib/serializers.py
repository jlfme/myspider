#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-03-13 21:45:18
# ---------------------------------------


import pickle
import umsgpack


class BaseSerializer(object):

    def loads(self, s):
        raise NotImplemented

    def dumps(self, obj):
        raise NotImplemented


class PickleSerializer(BaseSerializer):

    def __init__(self):
        self.serializer = pickle

    def loads(self, s):
        return self.serializer.loads(s)

    def dumps(self, obj):
        return self.serializer.dumps(obj, protocol=-1)


class UMSGSerializer(BaseSerializer):

    def __init__(self):
        self.serializer = umsgpack

    def loads(self, s):
        return self.serializer.loads(s)

    def dumps(self, obj):
        return self.serializer.dumps(obj, protocol=-1)
