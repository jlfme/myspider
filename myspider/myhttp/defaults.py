#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-02-10 22:00:18
# ---------------------------------------


# 保持长连接
KEEP_ALIVE_ENABLED = True

# 自动跳转
FOLLOW_LOCATION_ENABLED = False
# 最大重定向数
MAX_REDIRECT_NUMS = 5

# 启用cookies
COOKIES_ENABLED = False

# 超时设置
TIMEOUT = 30
DNS_TIMEOUT = 3600
CONNECT_TIMEOUT = 30

# 启用代理
HTTP_PROXY_ENABLED = True
# 代理配置, 启用代理时使用这个配置
HTTP_PROXY_INFO = {
    "type": 5,
    "url": "10.10.10.4:1080"
}


# 默认headers
REQUEST_HEADERS = {
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

# 默认的UA处理类
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0"

# # 默认的UA处理类
USER_AGENT_CLASS = 'myspider.myhttp.useragent.RandomUserAgent'
