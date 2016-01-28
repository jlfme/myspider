#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-01-28 21:07:18
# ---------------------------------------


# We should ignore SIGPIPE when using pycurl.NOSIGNAL - see
# the libcurl tutorial for more info.
try:
    import signal
    from signal import SIGPIPE, SIGKILL, SIG_IGN
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)

except ImportError:
    print("error")

import pycurl
import certifi
import chardet
from io import BytesIO
from urllib.parse import urlencode

from myspider.utils.log import Logger
from myspider.myhttp.useragent import RandomUserAgent
from myspider.myhttp.request import Request
from myspider.myhttp.response import Response
from myspider.myhttp.exceptions import ParseHeaderException


logger = Logger.get_logger('AsyncHTTPClient', Logger.INFO, 'console')


class AsyncHTTPClient(object):

    def __init__(self, request_queue, max_clients=10,
                 handle_response=None, handle_request_error=None):

        self.request_queue = request_queue
        self._multi = pycurl.CurlMulti()
        self._curls = [pycurl.Curl() for _ in range(max_clients)]
        self._freelist = self._curls[:]        # free curl list
        self.handle_response = handle_response            # callback, handle response
        self.handle_request_error = handle_request_error    # callback, handle request error
        self._config = dict(user_agent=RandomUserAgent.agent(),
                            handle_cookies=True,
                            dns_timeout=3600,
                            keep_alive=True,
                            handle_https=True,
                            max_redirs=5,
                            timeout=5,
                            connect_timeout=5,
                            encoding="gzip",
                            proxy={"status": False,
                                   "value": {"type": 5, "address": "10.10.10.4:1080"}})
        self.headers = {
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        self._init_curl_config()

    def _init_curl_config(self):
        """initial configuration,  """

        # pycurl bug
        dummy_curl_handle = pycurl.Curl()
        self._multi.add_handle(dummy_curl_handle)
        self._multi.remove_handle(dummy_curl_handle)

        for curl in self._curls:
            curl.setopt(pycurl.FOLLOWLOCATION, 1)
            curl.setopt(pycurl.NOSIGNAL, 1)
            curl.setopt(pycurl.USERAGENT, self._config["user_agent"])
            curl.setopt(pycurl.DNS_CACHE_TIMEOUT, self._config["dns_timeout"])
            if self._config["handle_cookies"]:
                curl.setopt(pycurl.COOKIEJAR, "cookie_file_name")
                curl.setopt(pycurl.COOKIEFILE, "cookie_file_name")
            if not self._config["keep_alive"]:
                curl.setopt(pycurl.FORBID_REUSE, 1)  # keepalive socket
            if self._config["handle_https"]:
                curl.setopt(pycurl.CAINFO, certifi.where())  # for https
            if self._config["proxy"]["status"]:  # proxy setting
                proxy_type = self._config["proxy"]["value"]["type"]
                address = self._config["proxy"]["value"]["address"]

                if proxy_type == 1:
                    curl.setopt(pycurl.PROXYTYPE, 1)
                    curl.setopt(pycurl.PROXY, address)  # http proxy
                elif proxy_type == 5:
                    curl.setopt(pycurl.PROXYTYPE, 5)
                    curl.setopt(pycurl.PROXY, address)  # socks5 porxy
            curl.setopt(pycurl.MAXREDIRS, self._config["max_redirs"])  # http redirect
            curl.setopt(pycurl.TIMEOUT, self._config["timeout"])
            curl.setopt(pycurl.CONNECTTIMEOUT, self._config["connect_timeout"])
            curl.setopt(pycurl.ENCODING, self._config["encoding"])  # HTTP data is compressed

    @staticmethod
    def _get_detail_info(curl):
        """获取其他详细信息"""
        if not isinstance(curl, pycurl.Curl):
            raise TypeError("curl_obj必须是Curl的对象")
        detail_info = dict(
            effective_url=curl.getinfo(pycurl.EFFECTIVE_URL),              # 返回地址
            primary_ip=curl.getinfo(pycurl.PRIMARY_IP),                    # 返回IP地址
            http_code=curl.getinfo(pycurl.HTTP_CODE),                      # 返回的HTTP状态码
            total_time=curl.getinfo(pycurl.TOTAL_TIME),                    # 传输结束所消耗的总时间
            namelookup_time=curl.getinfo(pycurl.NAMELOOKUP_TIME),          # DNS解析所消耗的时间
            connect_time=curl.getinfo(pycurl.CONNECT_TIME),                # 建立连接所消耗的时间
            pretransfer_time=curl.getinfo(pycurl.PRETRANSFER_TIME),        # 从建立连接到准备传输所消耗的时间
            starttransfer_time=curl.getinfo(pycurl.STARTTRANSFER_TIME),    # 从建立连接到传输开始消耗的时间
            redirect_time=curl.getinfo(pycurl.REDIRECT_TIME),              # 重定向所消耗的时间
            size_upload=curl.getinfo(pycurl.SIZE_UPLOAD),                  # 上传数据包大小
            size_download=curl.getinfo(pycurl.SIZE_DOWNLOAD),              # 下载数据包大小
            speed_download=curl.getinfo(pycurl.SPEED_DOWNLOAD),            # 平均下载速度
            speed_upload=curl.getinfo(pycurl.SPEED_UPLOAD),                # 平均上传速度
            header_size=curl.getinfo(pycurl.HEADER_SIZE))                  # HTTP头部大小
        logger.debug("%s%s", "detail_info:　　", detail_info)
        return detail_info

    def handle_result(self, curl):
        if not isinstance(curl, pycurl.Curl):
            raise TypeError("curl_obj必须是Curl的对象")

        curl.response_header.seek(0)
        curl.response_content.seek(0)
        headers_bytes = curl.response_header.getvalue()
        body = curl.response_content.getvalue()

        # 关闭缓冲区
        curl.response_header.close()
        curl.response_content.close()

        headers, cookies = self._cookies_and_headers(headers_bytes)
        detail_info = self._get_detail_info(curl)
        url = detail_info['effective_url']
        status_code = detail_info['http_code']

        request = curl.request
        response = Response(headers, status_code, body, url, request)

        logger.info("[%s]  %s  %s", "http_result", status_code, request.url)

        if self.handle_response is not None:                   # 回调函数, 处理response
            self.handle_response(response)
        elif request.callback is not None:
            request.callback(response)

    def _cookies_and_headers(self, headers_bytes):
        """ handle cookies and headers
        :param headers_bytes:
        :return:
        """

        headers = dict()
        cookies = list()
        headers_str = self._decode_headers(headers_bytes)

        if headers_str:
            lines = headers_str.split('\r\n\r\n')[-2].split("\r\n")[1:-1]
            for line in lines:
                header_line = line.split(":")
                if header_line[0].lower() == "set-cookie":
                    cookies.append({header_line[1]})
                else:
                    if len(header_line) == 2:
                        headers[header_line[0]] = header_line[1]
                    elif len(header_line) == 1:
                        headers[header_line[0]] = ''
                    else:
                        pass
        logger.debug("%s%s", "response_cookie:    ", cookies)
        return headers, cookies

    def _decode_headers(self, headers_bytes):
        """
        :param headers_bytes:

        :return:
        """

        headers_str = ''
        try:
            headers_str = headers_bytes.decode('ascii')
        except UnicodeDecodeError:
            try:
                headers_str = headers_bytes.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    headers_str = headers_bytes.decode('gbk')
                except UnicodeDecodeError:
                    try:
                        encoding = chardet.detect(headers_bytes)['encoding']
                        headers_str = headers_bytes.decode(encoding)
                    except UnicodeDecodeError:
                        print("headers_bytes", headers_bytes)
                        raise ParseHeaderException("解码headers出错了")

        logger.debug("%s---start---\n%s%s", "response_header:\n", headers_str, '---end---')
        return headers_str

    def _start_request(self, curl, request):
        """开始发送请求"""

        if not isinstance(request, Request):
            raise TypeError("request必须是Request对象")

        method = request.method
        self._make_request_header(curl, request.headers)

        try:
            if method == "GET" or method == "get":
                curl.setopt(pycurl.URL, request.url)
            elif method == "POST" or method == "post":
                curl.setopt(pycurl.URL, request.url)
                curl.setopt(pycurl.POSTFIELDS, urlencode(request.data))
            else:
                raise ValueError("request错误的请求方法")
        except Exception as e:
            raise Exception("start request error")

        curl.response_header = BytesIO()  # 返回的headers
        curl.response_content = BytesIO()  # 返回的网页内容
        curl.setopt(pycurl.HEADERFUNCTION, curl.response_header.write)
        curl.setopt(pycurl.WRITEFUNCTION, curl.response_content.write)
        curl.request = request                             # 将当前request传给client，以便于以后调用

    def _make_request_header(self, curl, headers):
        if headers is not None:
            headers.update(self.headers)
        else:
            headers = self.headers
        headers_list = []
        for key in headers:
            line = ": ".join([key, headers[key]])
            headers_list.append(line)
        logger.debug("%s%s", "request_cookie:   ", headers_list)
        curl.setopt(pycurl.HTTPHEADER, headers_list)

    def start(self):
        """main loop"""
        while True:
            while self._freelist and self.request_queue.qsize() > 0:
                curl = self._freelist.pop()
                request = self.request_queue.get()
                if request:
                    self._start_request(curl, request)           # send request
                    self._multi.add_handle(curl)
            while True:
                ret, num_handles = self._multi.perform()
                if ret != pycurl.E_CALL_MULTI_PERFORM:
                    break
            while True:
                num_q, ok_list, err_list = self._multi.info_read()
                for c in ok_list:
                    self.handle_result(c)
                    self._multi.remove_handle(c)
                    self._freelist.append(c)
                for c, errno, errmsg in err_list:

                    if self.handle_request_error is not None:
                        self.handle_request_error(c.request, errmsg)
                    else:
                        logger.info("[%s]  %s  %s", "HTTP_STATUS", c.request.url, errmsg)
                    self._multi.remove_handle(c)
                    self._freelist.append(c)
                if num_q == 0:
                    break
            self._multi.select(5.0)
