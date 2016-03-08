#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-01-28 21:07:18
# ---------------------------------------


"""
    We should ignore SIGPIPE when using pycurl.NOSIGNAL - see
    the libcurl tutorial for more info.
"""
try:
    import signal
    from signal import SIGPIPE, SIGKILL, SIG_IGN
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)
except ImportError:
    raise ImportError("import signal module error")

import pycurl
import certifi

from myspider.myhttp import defaults, processor
from myspider.utils.log import Logger
from myspider.myhttp.middlewares import MiddlewareManager


logger = Logger.get_logger('AsyncHTTPClient', Logger.INFO, 'console')


# CURL参数和默认配置的映射
CURL_PARAMS_MAP = {
    'CONTENT_ENCODING': (pycurl.ENCODING, 'gzip'),
    'HTTPS_ENABLED': (pycurl.CAINFO, certifi.where()),
    'NOSIGNAL': (pycurl.NOSIGNAL, 1),
    'DNS_TIMEOUT': (pycurl.DNS_CACHE_TIMEOUT, None),
    'MAX_REDIRECT_NUMS': (pycurl.MAXREDIRS, None),
    'TIMEOUT': (pycurl.TIMEOUT, None),
    'CONNECT_TIMEOUT': (pycurl.CONNECTTIMEOUT, None),
}


class CurlFactory(object):

    @classmethod
    def new_curl_from_settings(cls, **settings):
        """通过配置文件创建pycurl对象"""
        curl = pycurl.Curl()
        for k, v in CURL_PARAMS_MAP.items():
            if v[1] is not None:
                curl.setopt(v[0], v[1])
            elif v[1] is None and settings.get(k, False):
                params, value = v[0], settings[k]
                curl.setopt(params, value)
        if settings.get('COOKIES_ENABLED', False):
            curl.setopt(pycurl.COOKIEJAR, 'cookies_file')
            curl.setopt(pycurl.COOKIEFILE, 'cookies_file')
        if settings.get('HTTP_PROXY_ENABLED', False):
            if settings.get('HTTP_PROXY_INFO', False):
                curl.setopt(pycurl.PROXYTYPE, settings['HTTP_PROXY_INFO']['type'])
                curl.setopt(pycurl.PROXY, settings['HTTP_PROXY_INFO']['url'])
        if settings.get('FOLLOW_LOCATION_ENABLED', False):
            curl.setopt(pycurl.FOLLOWLOCATION, 1)
        if not settings.get('KEEP_ALIVE_ENABLED', False):
            curl.setopt(pycurl.FORBID_REUSE, 1)
        return curl


class AsyncHTTPClient(object):

    def __init__(self, request_queue, max_clients=10,
                 response_handler=None, request_error_handler=None, settings=None):
        self.request_queue = request_queue
        self._multi = pycurl.CurlMulti()
        self.response_handler = response_handler              # callback, handle response
        self.request_error_handler = request_error_handler    # callback, handle request error
        self.settings = self._read_settings(settings)

        # create curl object by settings
        self._curls = [CurlFactory.new_curl_from_settings(**self.settings) for _ in range(max_clients)]
        self._freelist = self._curls[:]

        # init request processor and response processor
        self.request_processor = processor.RequestProcessor(self.settings)
        self.response_processor = processor.ResponseProcessor()

        # middleware
        self.middleware = MiddlewareManager.from_setting(self.settings)

    @staticmethod
    def _read_settings(settings):
        # read default settings

        this_settings = {}
        for key in dir(defaults):
            if key.isupper():
                this_settings[key] = getattr(defaults, key)
        if isinstance(settings, dict):
            this_settings.update(settings)
        return this_settings

    def process_request(self, curl, request):
        """处理request"""

        # 根据全局settings设置request.settings
        settings = self.settings.copy()
        for key in request.settings.keys():
            if key in settings:
                settings.pop(key)
        request.settings.update(settings)
        # 调用中间件
        self.middleware.run_method('process_request', request, curl)

        # 开始发送request
        self.request_processor.process_request(curl, request)

    def process_response(self, curl):
        """处理response"""
        request = curl.request
        response = self.response_processor.process_response(curl)
        logger.info("[%s]  %s  %s", "http_result", response.status, request.url)
        # 调用中间件
        self.middleware.run_method('process_response', request, response)
        # 回调函数, 处理response
        if self.response_handler is not None:
            self.response_handler(response)

        elif request.callback is not None:
            request.callback(response)

    def start(self):
        """main loop"""
        while True:
            while self._freelist and self.request_queue.qsize() > 0:
                curl = self._freelist.pop()
                request = self.request_queue.get()

                # send request
                if request:
                    self.process_request(curl, request)
                    self._multi.add_handle(curl)
            while True:
                ret, num_handles = self._multi.perform()
                if ret != pycurl.E_CALL_MULTI_PERFORM:
                    break
            while True:
                num_q, ok_list, err_list = self._multi.info_read()
                for curl in ok_list:
                    self.process_response(curl)
                    self._multi.remove_handle(curl)
                    self._freelist.append(curl)
                for curl, errno, errmsg in err_list:
                    if self.request_error_handler is not None:
                        self.request_error_handler(curl.request, errmsg)
                    else:
                        logger.info("[%s]  %s  %s", "HTTP_STATUS", curl.request.url, errmsg)
                    self._multi.remove_handle(curl)
                    self._freelist.append(curl)
                if num_q == 0:
                    break
            self._multi.select(5.0)
