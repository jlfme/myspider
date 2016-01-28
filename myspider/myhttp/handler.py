#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-01-28 21:53:18
# ---------------------------------------


import re

from myspider.myhttp.exceptions import HandleResponseHeadersError
from myspider.myhttp.headers import Headers


_HTTP_STATUS_PATTERN = re.compile(r'(P?^HTTP/\d{1}\.\d{1})\s+(P?\d{3})', re.I)
_COOKIE_PATTERN = re.compile(r'set-cookie:\s*(P?.*)', re.I)
_HEADERS_PATTERN = re.compile(r'(P?^.*?):\s*(P?.*)')


class ResponseHeadersHandler(object):
    """handle response headers
    """

    def __init__(self, headers_bytes):
        self.headers_bytes = headers_bytes
        self._headers = Headers()
        self._http_code = 500
        self._http_version = 'HTTP/1.1'
        try:
            self._handle_headers()
        except:
            raise HandleResponseHeadersError(
                "handle response headers'{}' error".format(headers_bytes)
            )

    @property
    def http_code(self):
        return self._http_code

    @property
    def http_version(self):
        return self._http_version

    @property
    def headers(self):
        return self._headers

    def _handle_headers(self):
        cookies_list = list()
        lines = self.headers_bytes.splitlines()

        # http_status
        status = lines.pop(0).decode('ascii')
        m = re.match(_HTTP_STATUS_PATTERN, status)
        if m:
            self._http_version = m.groups()[0]
            self._http_code = int(m.groups()[1])

        # response headers
        for line in lines:
            line = self._decode(line)
            if line:
                if re.match(_COOKIE_PATTERN, line):
                    raw_data = re.match(_COOKIE_PATTERN, line).groups()[0]
                    self._headers.appendlist('Set-Cookie', raw_data)
                    cookies_list.append(raw_data)
                else:
                    m = re.match(_HEADERS_PATTERN, line)
                    if m:
                        key = m.groups()[0]
                        value = m.groups()[1]
                        self._headers.appendlist(key, value)

    def _decode(self, bytes, encoding='utf-8'):
        if encoding is None:
            encoding = 'utf-8'
        text = bytes.decode(encoding)
        return text
