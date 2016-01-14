#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-02-16 14:54:18
# ---------------------------------------


import time
from datetime import datetime

GMT_FORMAT = '%a, %d-%b-%Y %H:%M:%S GMT'


def gmt_to_datetime(gmt_str):
    """将GMT字符转换成datetime"""
    # 'Mon, 27-Aug-2085 02:57:11 GMT'
    return datetime.strptime(gmt_str, GMT_FORMAT)


def datetime_timestamp(datetime_str):
    """将datetime字符串转换成unix时间戳"""
    # dt为字符串 '2017-08-27 10:57:11'
    s = time.mktime(time.strptime(datetime_str, '%Y-%m-%d %H:%M:%S'))
    return int(s)


def now_unix_time():
    """获取当前系统的10位unix时间戳"""
    return int(time.time())


def now_utc_time():
    """获取GTM时间, 格式为：　Wed, 09-Aug-2017 19:55:25 GMT　"""
    return datetime.utcnow().strftime(GMT_FORMAT)


def utc2local(utc_st):
    """UTC时间转本地时间(+8:00）"""
    now_stamp = time.time()
    local_time = datetime.fromtimestamp(now_stamp)
    utc_time = datetime.utcfromtimestamp(now_stamp)
    offset = local_time - utc_time
    local_st = utc_st + offset
    return local_st


def gmt_to_unix_time(gmt_str):
    """GMT时间转换成unix时间戳"""
    # usage: 'Mon, 27-Aug-2085 02:57:11 GMT' ->　3649719431
    gmt = gmt_to_datetime(gmt_str)
    local = utc2local(gmt)
    unix = datetime_timestamp(str(local))
    return unix


if __name__ == "__main__":
    ok = gmt_to_datetime('Mon, 27-Aug-2085 02:57:11 GMT')
    print(ok)
    print(type(ok))
    print(utc2local(ok))

    unix = gmt_to_unix_time('Wed, 09-Aug-2017 22:47:41 GMT')
    print(unix)

    ok = now_unix_time()

    print(ok, ok+100)
