#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-02-15 22:40:18
# ---------------------------------------


from io import BytesIO
import pycurl
from myspider.utils.python import load_object
from myspider.myhttp.response import Response
from myspider.myhttp.headers import ResponseHeaders


class RequestMiddleware(object):
    """处理request"""

    def __init__(self, settings):
        self.settings = settings

    @classmethod
    def from_settings(cls, settings):
        return cls(settings=settings)

    def process_request(self, curl, request):
        curl.response_header = BytesIO()   # 返回的headers
        curl.response_content = BytesIO()  # 返回的网页内容
        curl.setopt(pycurl.HEADERFUNCTION, curl.response_header.write)
        curl.setopt(pycurl.WRITEFUNCTION, curl.response_content.write)
        curl.request = request             # 将request对象绑定到curl上，以便以后调用

        print(hasattr(curl, 'request'))
        # handle request headers
        default_headers = self.settings.get('REQUEST_HEADERS', {})
        if request.headers is not None:
            headers = request.headers
            if not isinstance(headers, dict):
                raise TypeError("'{headers} must be a dict'".format(headers=request.headers))
            headers.update(default_headers)
        else:
            headers = default_headers
        headers_list = [": ".join([k, v]) for k, v in headers.items()]
        print(headers_list)
        curl.setopt(pycurl.HTTPHEADER, headers_list)

        # handle request user_agent
        if self.settings.get('USER_AGENT_CLASS', None):
            user_agent_cls = load_object(self.settings['USER_AGENT_CLASS'])
            if not hasattr(user_agent_cls, 'agent'):
                raise NotImplementedError
            else:
                user_agent = user_agent_cls.agent()
                curl.setopt(pycurl.USERAGENT, user_agent)
        return None


class ResponseMiddleware(object):
    """处理response"""

    def process_response(self, curl):
        curl.response_header.seek(0)
        curl.response_content.seek(0)

        headers_bytes = curl.response_header.getvalue()
        body = curl.response_content.getvalue()
        detail = self._response_detail(curl)
        url = detail['effective_url']
        http_code = detail['http_code']
        headers = ResponseHeaders(headers_bytes)

        print(body)

        request = curl.request
        self._process_close(curl)
        return Response(headers=None, status_code=http_code, body=body, url=url, request=request)

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
        """获取curl详细信息"""
        detail = dict(
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
        return detail
