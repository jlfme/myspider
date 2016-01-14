#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-02-16 15:08:18
# ---------------------------------------


import chardet
from pyquery import PyQuery


class Response(object):

    def __init__(self, headers, status_code, body, url, request=None):
        self._headers = headers
        self._status_code = status_code
        self._body = body
        self._url = url
        self._request = request

    @property
    def headers(self):
        return self._headers

    @property
    def meta(self):
        try:
            return self.request.meta
        except AttributeError:
            raise AttributeError(
                "Response.meta not available, this response "
                "is not tied to any request"


            )

    @property
    def status_code(self):
        return self._status_code

    @property
    def body(self):
        return self._body

    @property
    def url(self):
        return self._url

    @property
    def request(self):
        return self._request

    def text(self, encoding=None):
        _text = None
        if encoding:
            _text = self._body.decode(encoding, 'ignore')
        else:
            encoding_detect = chardet.detect(self._body)
            if encoding_detect['confidence'] > 0.9:
                _text = self._body.decode(encoding_detect['encoding'])
            else:
                raise ResponseAutoDecodeError("自动解码出错了，请手动指定编码")
        return _text

    def doc(self, encoding=None):
        """
        :rtype: PyQuery
        :return: PyQuery
        """
        html = self.text(encoding)
        return PyQuery(html)


class ResponseAutoDecodeError(Exception):
    """自动解码错误"""
    pass
