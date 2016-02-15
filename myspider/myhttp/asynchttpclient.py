#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-01-28 21:07:18
# ---------------------------------------


try:
    import signal
    from signal import SIGPIPE, SIGKILL, SIG_IGN
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)
except ImportError:
    raise ImportError("import signal module error")


import pycurl
import certifi

from myspider.myhttp import defaults
from myspider.myhttp import processor
from myspider.utils.log import Logger

logger = Logger.get_logger('AsyncHTTPClient', Logger.INFO, 'console')


# CURL参数和默认配置的映射
CURL_PARAMS_MAP = {
    # 'FOLLOWLOCATION': (pycurl.FOLLOWLOCATION, 1), #　自动跳转
    'NOSIGNAL': (pycurl.NOSIGNAL, 1),
    # 'KEEP_ALIVE_ENABLED': (pycurl.FORBID_REUSE, 1),
    'CONTENT_ENCODING': (pycurl.ENCODING, 'gzip'),
    'HTTPS_ENABLED': (pycurl.CAINFO, certifi.where()),
    'DNS_TIMEOUT': (pycurl.DNS_CACHE_TIMEOUT, None),
    'MAX_REDIRECT_NUMS': (pycurl.MAXREDIRS, None),
    'TIMEOUT': (pycurl.TIMEOUT, None),
    'CONNECT_TIMEOUT': (pycurl.CONNECTTIMEOUT, None)
}


class CurlFactory(object):

    @staticmethod
    def from_settings(settings):
        """通过配置文件创建pycurl对象"""
        curl = pycurl.Curl()

        for k, v in CURL_PARAMS_MAP.items():
            if v[1] is not None:
                params, value = v[0], v[1]
                curl.setopt(params, value)
            if v[1] is None and settings.get(k, None):
                params, value = v[0], settings[k]
                curl.setopt(params, value)
        if settings.get('COOKIES_ENABLED', None):
            curl.setopt(pycurl.COOKIEJAR, 'cookies_file')
            curl.setopt(pycurl.COOKIEFILE, 'cookies_file')
        if settings.get('HTTP_PROXY', None):
            curl.setopt(pycurl.PROXYTYPE, settings['HTTP_PROXY']['type'])
            curl.setopt(pycurl.PROXY, settings['HTTP_PROXY']['url'])
        return curl


class AsyncHTTPClient(object):

    def __init__(self, request_queue, max_clients=10,
                 handle_response=None, handle_request_error=None, settings=None):
        self.request_queue = request_queue
        self._multi = pycurl.CurlMulti()
        self.handle_response = handle_response              # callback, handle response
        self.handle_request_error = handle_request_error    # callback, handle request error
        self.settings = self._read_settings(settings)

        # create curl object by settings
        self._curls = [CurlFactory.from_settings(self.settings) for _ in range(max_clients)]
        self._freelist = self._curls[:]

        # init request processor and response processor
        self.request_processor = processor.RequestProcessor.from_settings(self.settings)
        self.response_processor = processor.ResponseProcessor()

        # middleware



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

    def process_response(self, curl):
        """处理response"""
        request = curl.request
        response = self.response_processor.process_response(curl)
        logger.info("[%s]  %s  %s", "http_result", response.status_code, request.url)

        if self.handle_response is not None:              # 回调函数, 处理response
            self.handle_response(response)
        elif request.callback is not None:
            request.callback(response)

    def process_request(self, curl, request):
        """request"""

        self.request_processor.process_request(curl, request)

    def start(self):
        """main loop"""
        while True:
            while self._freelist and self.request_queue.qsize() > 0:
                curl = self._freelist.pop()
                request = self.request_queue.get()
                if request:
                    self.process_request(curl, request)           # send request
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
                    if self.handle_request_error is not None:
                        self.handle_request_error(curl.request, errmsg)
                    else:
                        logger.info("[%s]  %s  %s", "HTTP_STATUS", curl.request.url, errmsg)
                    self._multi.remove_handle(curl)
                    self._freelist.append(curl)
                if num_q == 0:
                    break
            self._multi.select(5.0)

