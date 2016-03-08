#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-02-15 22:40:18
# ---------------------------------------


import copy
import pycurl
from io import BytesIO
from urllib.parse import urlencode

from myspider.myhttp.handler import ResponseHeadersHandler
from myspider.myhttp.headers import Headers
from myspider.myhttp.request import Request
from myspider.myhttp.response import Response
from myspider.utils.log import Logger
from myspider.utils.python import load_object


logger = Logger.get_logger('LLLL', Logger.DEBUG, 'console')


class RequestProcessor(object):
    """处理request"""

    def __init__(self, settings):
        self.settings = settings

    @classmethod
    def from_settings(cls, settings):
        return cls(settings=settings)

    def process_request(self, curl, request):
        if not isinstance(request, Request):
            raise TypeError("'{}' must be an instance of Request".format(request))
        self._wrap_request(curl, request)

    def _wrap_request(self, curl, request):
        """将request的请求信息打包转换成pycurl参数

        """
        method = request.method
        if method.lower() == "get":
            try:
                curl.setopt(pycurl.URL, request.url)
            except Exception as e:
                print(method, request.url)

        elif method.lower() == "post":
            curl.setopt(pycurl.URL, request.url)
            curl.setopt(pycurl.POSTFIELDS, urlencode(request.data))
        else:
            raise ValueError("request.method must be 'GET' or 'POST'")

        # handle request headers
        headers = Headers(self.settings.get('REQUEST_HEADERS', {}))
        if request.headers is not None:
            if not isinstance(request.headers, dict):
                raise TypeError(
                    "'{headers} must be a dict'".format(headers=request.headers)
                )
            headers.update(request.headers)

        # handle request user_agent
        if not headers.get('user-agent', None):
            if self.settings.get('USER_AGENT_CLASS', None):
                user_agent_cls = load_object(self.settings['USER_AGENT_CLASS'])
                if not hasattr(user_agent_cls, 'agent'):
                    raise NotImplementedError
                else:
                    user_agent = user_agent_cls.agent()
                    headers['User-Agent'] = user_agent

        headers_list = headers.to_unicode_list()
        curl.setopt(pycurl.HTTPHEADER, headers_list)

        # callback function for headers and body
        curl.response_header = BytesIO()  # 返回的headers
        curl.response_content = BytesIO()  # 返回的网页内容
        curl.setopt(pycurl.HEADERFUNCTION, curl.response_header.write)
        curl.setopt(pycurl.WRITEFUNCTION, curl.response_content.write)
        curl.request = request  # 将request对象绑定到curl上，以便以后调用
        return None


class ResponseProcessor(object):
    """处理response

    """

    def process_response(self, curl):
        curl.response_header.seek(0)
        curl.response_content.seek(0)

        headers_bytes = curl.response_header.getvalue()
        body = curl.response_content.getvalue()
        detail = self._response_detail(curl)
        url = detail['effective_url']
        status = detail['http_code']

        headers = ResponseHeadersHandler(headers_bytes).headers
        request = copy.deepcopy(curl.request)
        self._process_close(curl)

        return Response(url,
                        status,
                        headers,
                        body,
                        request)

    def _process_close(self, curl):
        # 关闭缓冲区
        attr_list = ['response_header', 'response_content', 'request']
        if hasattr(curl, 'response_header'):
            curl.response_header.close()
        if hasattr(curl, 'response_content'):
            curl.response_content.close()
        for attr in attr_list:
            if hasattr(curl, attr):
                delattr(curl, attr)

    def _response_detail(self, curl):
        """  http response detail information
        :param curl: The `~pycurl.PyCurl` instance

        """
        return dict(
            effective_url=curl.getinfo(pycurl.EFFECTIVE_URL),  # 返回地址
            primary_ip=curl.getinfo(pycurl.PRIMARY_IP),  # 返回IP地址
            http_code=curl.getinfo(pycurl.HTTP_CODE),  # 返回的HTTP状态码
            total_time=curl.getinfo(pycurl.TOTAL_TIME),  # 传输结束所消耗的总时间
            namelookup_time=curl.getinfo(pycurl.NAMELOOKUP_TIME),  # DNS解析所消耗的时间
            connect_time=curl.getinfo(pycurl.CONNECT_TIME),  # 建立连接所消耗的时间
            pretransfer_time=curl.getinfo(pycurl.PRETRANSFER_TIME),  # 从建立连接到准备传输所消耗的时间
            starttransfer_time=curl.getinfo(pycurl.STARTTRANSFER_TIME),  # 从建立连接到传输开始消耗的时间
            redirect_time=curl.getinfo(pycurl.REDIRECT_TIME),  # 重定向所消耗的时间
            size_upload=curl.getinfo(pycurl.SIZE_UPLOAD),  # 上传数据包大小
            size_download=curl.getinfo(pycurl.SIZE_DOWNLOAD),  # 下载数据包大小
            speed_download=curl.getinfo(pycurl.SPEED_DOWNLOAD),  # 平均下载速度
            speed_upload=curl.getinfo(pycurl.SPEED_UPLOAD),  # 平均上传速度
            header_size=curl.getinfo(pycurl.HEADER_SIZE))  # HTTP头部大小
        # logger.debug("%s%s", "detail_info:　　", detail_info)
