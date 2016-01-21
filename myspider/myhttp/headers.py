#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-01-15 20:12:18
# ---------------------------------------


import re
from w3lib.http import headers_dict_to_raw
from myspider.utils.datastructs import CaselessDict
from myspider.utils.python import to_unicode


class ResponseHeaders(object):

    def __init__(self, headers_byte, domain=None):
        self.headers_byte = headers_byte
        self.domain = domain
        self.headers_str = ""
        self.cookies = {}
        try:
            self.decode_headers()
        except Exception as e:
            print(self.headers_byte)

        self._http_code = 404
        self._http_version = 'HTTP/1.1'

    @property
    def http_code(self):
        return self._http_code

    @property
    def http_version(self):
        return self._http_version

    def decode_headers(self):
        self.headers_str = self.headers_byte.decode('ascii')
        if self.headers_str:
            status = self.headers_str.split('\r\n\r\n')[0].split("\r\n")[0]
            lines = self.headers_str.split('\r\n\r\n')[0].split("\r\n")[1:-1]
            self._http_version = re.search(r'^HTTP/\d{1}\.\d{1}', status).group(0)
            self._http_code = re.search(r'\d{3}', status).group(0)
            headers = dict()
            cookies = list()
            for line in lines:
                header_line = line.split(": ")
                if header_line[0].lower() == "set-cookie":
                    cookies.append(header_line[1])
                else:
                    if len(header_line) == 2:
                        headers[header_line[0]] = header_line[1]
                    elif len(header_line) == 1:
                        headers[header_line[0]] = ''
                    else:
                        pass
            self.handle_cookies(cookies)

            # print(self.headers_str)
            print(self.http_code, self.http_version, headers, cookies)

    def handle_cookies(self, cookies_list):

        for cookies in cookies_list:
            print('COOKIES----', cookies)
            self._parse_cookies(cookies)

    def _parse_cookies(self, cookies_str):

        max_age_pattern = re.compile(r'max-age=(P?\d+)', re.I)
        expires_pattern = re.compile(r'expires=(P?.*)', re.I)
        path_pattern = re.compile(r'path=(P?.*)', re.I)
        http_only_pattern = re.compile(r'HttpOnly', re.I)
        secure_pattern = re.compile(r'(P?Secure)', re.I)
        domain_pattern = re.compile(r'domain=(P?.*)', re.I)

        cookies_list = cookies_str.split("; ")
        print(cookies_list, len(cookies_list))

        item = dict(name='',
                    value='',
                    max_age='session',
                    expires=None,
                    path='/',
                    http_only=False,
                    secure=False,
                    domain=self.domain)
        for cookie in cookies_list:
            # max-age
            if re.match(max_age_pattern, cookie):
                item['max_age'] = re.match(max_age_pattern, cookie).groups()[0]
            # expires
            elif re.match(expires_pattern, cookie):
                item['expires'] = re.match(expires_pattern, cookie).groups()[0]
            # path
            elif re.match(path_pattern, cookie):
                item['path'] = re.match(path_pattern, cookie).groups()[0]
            # http_only
            elif re.search(http_only_pattern, cookie):
                item['http_only'] = True
            # secure
            elif re.match(secure_pattern, cookie):
                item['secure'] = True
            # domain
            elif re.match(domain_pattern, cookie):
                item['domain'] = re.match(domain_pattern, cookie).groups()[0]
            else:
                print('NONE------', cookie)


class Headers(CaselessDict):
    """Case insensitive http headers dictionary"""

    def __init__(self, seq=None, encoding='utf-8'):
        self.encoding = encoding
        super(Headers, self).__init__(seq)

    def normkey(self, key):
        """Normalize key to bytes"""
        return self._tobytes(key.title())

    def normvalue(self, value):
        """Normalize values to bytes"""
        if value is None:
            value = []
        elif isinstance(value, (str, bytes)):
            value = [value]
        elif not hasattr(value, '__iter__'):
            value = [value]

        return [self._tobytes(x) for x in value]

    def _tobytes(self, x):
        if isinstance(x, bytes):
            return x
        elif isinstance(x, str):
            return x.encode(self.encoding)
        elif isinstance(x, int):
            return str(x).encode(self.encoding)
        else:
            raise TypeError('Unsupported value type: {}'.format(type(x)))

    def __getitem__(self, key):
        try:
            return super(Headers, self).__getitem__(key)[-1]
        except IndexError:
            return None

    def get(self, key, def_val=None):
        try:
            return super(Headers, self).get(key, def_val)[-1]
        except IndexError:
            return None

    def getlist(self, key, def_val=None):
        try:
            return super(Headers, self).__getitem__(key)
        except KeyError:
            if def_val is not None:
                return self.normvalue(def_val)
            return []

    def setlist(self, key, list_):
        self[key] = list_

    def setlistdefault(self, key, default_list=()):
        return self.setdefault(key, default_list)

    def appendlist(self, key, value):
        lst = self.getlist(key)
        lst.extend(self.normvalue(value))
        self[key] = lst

    def items(self):
        return list(self.iteritems())

    def iteritems(self):
        return ((k, self.getlist(k)) for k in self.keys())

    def values(self):
        return [self[k] for k in self.keys()]

    def to_string(self):
        return headers_dict_to_raw(self)

    def to_unicode_list(self):
        """Retrun headers as list
        """
        return [to_unicode(b': '.join([key, b','.join(value)]))
                for key, value in self.items()]

    def to_unicode_dict(self):
        """ Return headers as a CaselessDict with unicode keys
        and unicode values. Multiple values are joined with ','.
        """
        return CaselessDict(
            (to_unicode(key, encoding=self.encoding),
             to_unicode(b','.join(value), encoding=self.encoding))
            for key, value in self.items())

    def __copy__(self):
        return self.__class__(self)
    copy = __copy__
