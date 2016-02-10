#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-02-10 22:00:18
# ---------------------------------------


# COOKIES_ENABLED = True
DNS_TIMEOUT = 3600
MAX_REDIRECT_NUMS = 5
TIMEOUT = 15
CONNECT_TIMEOUT = 15

HTTP_PROXY = {
    "type": 5,
    "url": "10.10.10.4:1080"
}

REQUEST_HEADERS = {
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

# 默认的user-agent类
USER_AGENT_CLASS = 'myspider.myhttp.useragent.RandomUserAgent'


MIDDLEWARES_BASE = {
    'myspider.myhttp.middlewares.cookies.RedisCookiesMiddleware': True
}
