#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-02-16 14:59:18
# ---------------------------------------


from myspider.myhttp.headers import Headers


class Request(object):
    def __init__(self, url, method="GET", data=None, headers=None,
                 meta=None, cookies=None, dont_filter=True, callback=None, settings=None):
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
        self._headers = Headers(headers or {}, encoding='utf-8')
        self._meta = meta
        self._cookies = cookies or {}
        self._dont_filter = dont_filter
        self._callback = callback
        self._settings = settings or {}

    @property
    def data(self):
        return self._data

    @property
    def dont_filter(self):
        return self._dont_filter

    @property
    def method(self):
        return self._method

    @property
    def cookies(self):
        return self._cookies

    @property
    def settings(self):
        return self._settings

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

    @property
    def url(self):
        return self._url

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, callback):
        self._callback = callback
