#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-02-16 14:59:18
# ---------------------------------------


class Request(object):
    def __init__(self, url, method="GET", data=None, headers=None, meta=None, cookies=None, callback=None):
        """
        :param url:
        :param method:
        :param data: if method="POST", please give the data
        :param headers:
        :param cookies:
        """
        self._url = url
        self._method = method
        self._data = data
        self._headers = headers
        self._meta = meta
        self._cookies = cookies
        self._callback = callback

    @property
    def data(self):
        return self._data

    @property
    def method(self):
        return self._method

    @property
    def meta(self):
        if self._meta is None:
            self._meta = {}
        return self._meta

    @method.setter
    def method(self, method):
        if isinstance(method, str):
            self._method = method
        else:
            raise TypeError('%s method must be str, got %s:' % (type(self).__name__, type(method).__name__))

    @property
    def headers(self):
        return self._headers

    def add_header(self, header):
        """
        :param header: {"Referer": "http://www.example.com", "User-Agent": "easyspider"}
        :return:
        """
        for k, v in header:
            pass

    @property
    def url(self):
        return self._url

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, callback):
        self._callback = callback
