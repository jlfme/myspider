#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-02-15 22:49:18
# ---------------------------------------


from collections import defaultdict
from myspider.utils.python import load_object
from myspider.myhttp.exceptions import ExecuteMiddlewareError


class MiddlewareManager(object):

    def __init__(self, *middleware_list):
        self.methods = defaultdict(list)
        for middleware in middleware_list:
            self._add_middleware(middleware)

    @classmethod
    def from_setting(cls, settings):
        class_path_list = sorted(settings.get('MIDDLEWARES_BASE', {}).items(), key=lambda d: d[1])
        middleware_list = []
        for class_path in class_path_list:
            class_path = class_path[0]
            mw_cls = load_object(class_path)
            mw = mw_cls()
            middleware_list.append(mw)
        return cls(*middleware_list)

    def _add_middleware(self, middleware):
        if hasattr(middleware, 'process_request'):
            self.methods['process_request'].append(middleware.process_request)
        if hasattr(middleware, 'process_response'):
            self.methods['process_response'].append(middleware.process_response)

    def run_method(self, method_name, *args):
        """运行指定的方法名"""
        methods = self.methods[method_name]
        for method in methods:
            try:
                method(*args)
            except:
                raise ExecuteMiddlewareError(
                    "execute '{method} error'".format(method=method)
                )
