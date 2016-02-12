#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-02-16 15:08:18
# ---------------------------------------


import re
import chardet
from pyquery import PyQuery
from myspider.myhttp.headers import Headers
from myspider.myhttp.exceptions import ResponseAutoDecodeError


_ENCODING_PATTERN = re.compile(r'.*?charset=(P?.*)', re.I)


class Response(object):

    def __init__(self, url, status=200, headers=None, body=b'', request=None):
        self._headers = headers or Headers({})
        self._status = int(status)
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
                "is not tied to any request")

    @property
    def status(self):
        return self._status

    @property
    def encoding(self):
        _encoding = None
        content_type = self.headers.get('Content-Type', None).decode('utf-8')
        if content_type:
            m = re.match(_ENCODING_PATTERN, content_type)
            if m:
                _encoding = m.groups()[0].lower()
        return _encoding

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
        html = self.text(encoding)
        doc = PyQuery(html)
        return doc
