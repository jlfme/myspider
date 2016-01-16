#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-01-16 20:19:18
# ---------------------------------------


import gzip
import threading
from io import BytesIO
import certifi
import pycurl
from urllib.parse import urlencode
from . request import Request
from . response import Response
from . useragent import RandomUserAgent


class HttpDownloader(threading.Thread):
    """多线程http下载器"""

    def __init__(self, request_queue, ip_queue, parse_callback=None):
        threading.Thread.__init__(self)
        self.client = HttpClient()
        self.request_queue = request_queue
        self.ip_queue = ip_queue
        self.parse_callback = parse_callback

    def run(self):
        address = self.ip_queue.pop()
        if address:
            address = address.decode("utf-8")
            self.client.set_proxy(address)

        while True:
            try:
                request = self.request_queue.get()
                if request:
                    response = self.client.start_request(request)
            except Exception as e:
                print(e)

                address = self.ip_queue.pop()
                if address:
                    address = address.decode("utf-8")
                    self.client.set_proxy(address)

            else:
                try:
                    self.parse_callback(response)
                except Exception as e:
                    print(e)

    @staticmethod
    def fetch(client_size, request_queue, ip_queue, parse_callback=None):
        for _ in range(client_size):
            d = HttpDownloader(request_queue, ip_queue, parse_callback)
            d.start()


class HttpClient(object):

    def __init__(self, keep_alive=True):
        self._client = pycurl.Curl()
        self._config = dict(user_agent=RandomUserAgent.agent(),
                            handle_cookies=False,
                            dns_timeout=3600,
                            keep_alive=keep_alive,
                            handle_https=True,
                            max_redirs=5,
                            timeout=20,
                            connect_timeout=20,
                            proxy={"status": False,
                                   "value": {"type": 1, "address": "http://42.243.203.61:8998"}})

        self.headers = [
            "Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding: gzip"
        ]

        self._last_request_url = None        # 上一次请求的url

    def _init_config(self, request):
        """初始化配置信息, 发送请求前必须调用"""

        if request.url == self._last_request_url:  # 比较这次和上次请求地址是否属于同一个域名
            self._client.setopt(pycurl.FORBID_REUSE, 0)  # 相同就保持长连接
        else:
            self._client.setopt(pycurl.FORBID_REUSE, 1)  # 不相同就断开连接

        if request.headers:                              # 处理headers
            self.headers = request.headers

        self._client.setopt(pycurl.FOLLOWLOCATION, 1)
        self._client.setopt(pycurl.USERAGENT, self._config["user_agent"])
        self._client.setopt(pycurl.DNS_CACHE_TIMEOUT, self._config["dns_timeout"])
        if self._config["handle_cookies"]:
            self._client.setopt(pycurl.COOKIEJAR, "cookie_file_name")
            self._client.setopt(pycurl.COOKIEFILE, "cookie_file_name")
        if not self._config["keep_alive"]:
            self._client.setopt(pycurl.FORBID_REUSE, 1)  # 完成交互后强制断开连接，不保持长连接

        if self._config["handle_https"]:
            self._client.setopt(pycurl.CAINFO, certifi.where())  # 用于https

        if self._config["proxy"]["status"]:                            # 设置代理
            proxy_type = self._config["proxy"]["value"]["type"]
            address = self._config["proxy"]["value"]["address"]
            if proxy_type == 1:
                self._client.setopt(pycurl.PROXYTYPE, 1)
                self._client.setopt(pycurl.PROXY, address)  # http代理
            elif proxy_type == 5:
                self._client.setopt(pycurl.PROXYTYPE, 5)
                self._client.setopt(pycurl.PROXY, address)  # socks5代理

        self._client.setopt(pycurl.MAXREDIRS, self._config["max_redirs"])       # 最大重定向数
        self._client.setopt(pycurl.TIMEOUT, self._config["timeout"])
        self._client.setopt(pycurl.CONNECTTIMEOUT, self._config["connect_timeout"])

        # self._client.setopt(pycurl.ENCODING, self._config["encoding"])  # 使用gzip编码下载 加快速度
        self._client.setopt(pycurl.HTTPHEADER, self.headers)            # 添加请求头 headers

    def _end_config(self, request):
        """发送请求结束后调用，做一些结束工作"""
        self._last_request_url = request.url

    def set_proxy(self, proxy_ip):
        """请给定代理ip地址和端口 例如：http://42.243.203.61:8998"""
        self._config["proxy"]["status"] = True
        self._config["proxy"]["value"]["address"] = proxy_ip

    def start_request(self, request):
        """
        # 通过给的request对象开始http请求
        :param request:  Request对象
        :return:  Response对象
        """
        response = None
        if not isinstance(request, Request):
            raise TypeError("request必须是Request对象")

        self._init_config(request)           # 初始化配置

        method = request.method
        if method == "GET" or method == "get":
            response = self._http_get(request)
        elif method == "POST" or method == "post":
            response = self._http_post(request)
        else:
            raise ValueError("request错误的请求方法")

        self._end_config(request)           # 结束处理

        return response

    def _http_get(self, request):

        if request.method != "GET" and request.method != "get":
            raise ValueError("request请求方法必须是GET")
        response_header = BytesIO()
        content = BytesIO()
        self._client.setopt(pycurl.URL, request.url)
        self._client.setopt(pycurl.HEADERFUNCTION, response_header.write)
        self._client.setopt(pycurl.WRITEFUNCTION, content.write)
        self._client.perform()
        return self._get_response(request, response_header, content)  # 处理请求然后返回response对象

    def _http_post(self, request):
        if request.method != "POST" and request.method != "post":
            raise ValueError("request请求方法必须是POST")
        if request.data is None:
            raise ValueError("request方法是POST时，data不能为空")

        response_header = BytesIO()
        content = BytesIO()
        self._client.setopt(pycurl.URL, request.url)
        self._client.setopt(pycurl.POSTFIELDS, urlencode(request.data))
        self._client.setopt(pycurl.HEADERFUNCTION, response_header.write)
        self._client.setopt(pycurl.WRITEFUNCTION, content.write)
        self._client.perform()
        return self._get_response(request, response_header, content)  # 处理请求然后返回response对象

    def _get_response(self, request, response_header, content):

        headers, cookies = self._get_cookies_and_headers(response_header)
        # print(cookies, headers)

        body = content.getvalue()

        body = self._undecode_response(headers, body)
        detail_info = self._get_detail_info()
        status_code = detail_info["http_code"]
        url = detail_info["effective_url"]
        response = Response(headers=headers,
                            status_code=status_code,
                            body=body,
                            url=url,
                            request=request)
        return response

    def _undecode_response(self, headers, body):
        """根据headers返回的压缩编码解压网页"""
        if "Content-Encoding" in headers.keys():
            if headers['Content-Encoding'].lower() == 'gzip':
                body = gzip.decompress(body)
        return body

    def _get_cookies_and_headers(self, response_header):
        """分析cookies和headers"""

        response_header.seek(0)
        status = response_header.readline().decode().strip()
        headers = dict()
        cookies = list()
        while True:
            line = response_header.readline().strip()
            if not line:
                break
            try:
                header_line = line.decode().split(": ")
                if header_line[0].lower() == "set-cookie":
                    cookies.append({header_line[1]})
                else:
                    headers[header_line[0]] = header_line[1]
            except Exception as e:
                pass
        return headers, cookies

    def _get_detail_info(self):
        """获取其他详细信息"""

        info = dict(
            effective_url=self._client.getinfo(pycurl.EFFECTIVE_URL),          # 返回地址
            primary_ip=self._client.getinfo(pycurl.PRIMARY_IP),                # 返回IP地址
            http_code=self._client.getinfo(pycurl.HTTP_CODE),                 # 返回的HTTP状态码
            total_time=self._client.getinfo(pycurl.TOTAL_TIME),                # 传输结束所消耗的总时间
            namelookup_time=self._client.getinfo(pycurl.NAMELOOKUP_TIME),           # DNS解析所消耗的时间
            connect_time=self._client.getinfo(pycurl.CONNECT_TIME),              # 建立连接所消耗的时间
            pretransfer_time=self._client.getinfo(pycurl.PRETRANSFER_TIME),     # 从建立连接到准备传输所消耗的时间
            starttransfer_time=self._client.getinfo(pycurl.STARTTRANSFER_TIME),   # 从建立连接到传输开始消耗的时间
            redirect_time=self._client.getinfo(pycurl.REDIRECT_TIME),             # 重定向所消耗的时间
            size_upload=self._client.getinfo(pycurl.SIZE_UPLOAD),               # 上传数据包大小
            size_download=self._client.getinfo(pycurl.SIZE_DOWNLOAD),             # 下载数据包大小
            speed_download=self._client.getinfo(pycurl.SPEED_DOWNLOAD),            # 平均下载速度
            speed_upload=self._client.getinfo(pycurl.SPEED_UPLOAD),              # 平均上传速度
            header_size=self._client.getinfo(pycurl.HEADER_SIZE),               # HTTP头部大小
        )
        return info

if __name__ == "__main__":
    client = HttpClient()
    ok = client.start_request(Request(url="http://www.youku.com"))
    print(ok.status_code, ok.url, ok.headers)
