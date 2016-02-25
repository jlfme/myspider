#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-02-19 22:55:18
# ---------------------------------------


from collections import defaultdict
from myspider.myhttp.headers import Headers
from myspider.myhttp.response import Response
from myspider.myhttp.cookies import CookieJar


class CookiesMiddleware(object):

    def __init__(self):
        self.jars = defaultdict(CookieJar)

    def process_request(self, request):
        jar = self.jars['cookie_jar']
        cookies = self._get_request_cookies(jar, request)
        for cookie in cookies:
            print('cookie:', cookie)
            jar.set_cookie_if_ok(cookie, request)

        request.headers.pop('Cookie', None)
        jar.add_cookie_header(request)
        print('cookie middleware', request.headers)

    def process_response(self, request, response):
        if request.meta.get('dont_merge_cookies', False):
            return response

        # extract cookies from Set-Cookie and drop invalid/expired cookies
        jar = self.jars['cookie_jar']
        jar.extract_cookies(response, request)
        return response

    def _format_cookie(self, cookie):

        # build cookie string
        cookie_str = '%s=%s' % (cookie['name'], cookie['value'])
        if cookie.get('path', None):
            cookie_str += '; Path=%s' % cookie['path']
        if cookie.get('domain', None):
            cookie_str += '; Domain=%s' % cookie['domain']
        return cookie_str

    def _get_request_cookies(self, jar, request):
        if isinstance(request.cookies, dict):
            cookie_list = [{'name': k, 'value': v} for k, v in request.cookies.items()]
        else:
            cookie_list = request.cookies
        cookies = [self._format_cookie(x) for x in cookie_list]
        headers = Headers({'Set-Cookie': cookies})
        response = Response(request.url, headers=headers)
        cookies = jar.make_cookies(response, request)
        return cookies
