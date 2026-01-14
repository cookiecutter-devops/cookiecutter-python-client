#!/usr/bin/env python
# -*- coding: utf-8 -*-
from {{cookiecutter.project_slug}}.common import http
from {{cookiecutter.project_slug}}.{{cookiecutter.api_version }} import images


class Client(object):
    def __init__(self, username=None, password=None, project=None, baseurl=None,
                 extensions=None, token=None, timings=False, http_log_debug=False, timeout=None,
                 insecure=False, cacert=None, return_response=False):
        self.client = http._construct_http_client(
            username=username,
            password=password,
            project=project,
            baseurl=baseurl,
            token=token,
            http_log_debug=http_log_debug,
            timeout=timeout,
            insecure=insecure,
            cacert=cacert,
            timings=timings,
            return_response=return_response
        )
        # extensions
        self.images = images.Controller(self)

        # Add in any extensions...
        if extensions:
            for extension in extensions:
                if extension.manager_class:
                    setattr(self, extension.name,
                            extension.manager_class(self))

    def authenticate(self):
        """认证客户端"""
        # self.client.authenticate()
        # 对于 Docker Registry，通常不需要显式认证
        # 可能需要实现特定的认证逻辑
        pass

    def get_timings(self):
        return self.client.get_timings()

    def reset_timings(self):
        self.client.reset_timings()
