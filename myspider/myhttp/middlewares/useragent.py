#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2016-02-28 23:10:18
# ---------------------------------------


from myspider.utils.python import load_object


class UserAgentMiddleware(object):

    def process_request(self, request, curl):
        # default headers
        headers = request.settings.get('REQUEST_HEADERS', None)
        if headers is not None:
            for k, v in headers.items():
                if k not in request.headers:
                    request.headers[k] = v

        # make user-agent
        ua = "Mozilla/5.0 (compatible; My_Spider/1.0)"
        if not request.headers.get('user-agent', None):
            if request.settings.get('USER_AGENT_CLASS', None):
                user_agent_cls = load_object(request.settings['USER_AGENT_CLASS'])
                if not hasattr(user_agent_cls, 'agent'):
                    raise NotImplementedError
                ua = user_agent_cls.agent()
            elif request.settings.get('DEFAULT_USER_AGENT', None):
                ua = request.settings.get('DEFAULT_USER_AGENT')
            request.headers['user-agent'] = ua
