#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-02-18 19:12:18
# ---------------------------------------


class ParseHeaderException(Exception):
    pass


class StartRequestError(Exception):
    pass


class HandleResponseHeadersError(Exception):
    pass


class ExecuteMiddlewareError(Exception):
    pass
