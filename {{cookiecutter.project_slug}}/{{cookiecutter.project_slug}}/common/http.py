#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import base64
import logging
import json
from six.moves.urllib.parse import urlparse
import requests
from {{cookiecutter.project_slug}}.common import exceptions
from {{cookiecutter.project_slug}}.common import utils


class HTTPClient(object):
    USER_AGENT = "{{cookiecutter.project_slug}}"

    def __init__(
            self,
            username,
            password,
            project,
            baseurl,
            token=None,
            headers=None,
            http_log_debug=False,
            timeout=None,
            insecure=False,
            cacert=None,
            timings=False,
            api_version=None,
            return_response=False
    ):
        """
        初始化 REST 客户端
        :param username: 用户名（如果需要基本认证）
        :param password: 密码（如果需要基本认证）
        :param project: 项目名称（如果需要项目认证）
        :param baseurl: API 基础 URL
        :param token: Bearer token（如果使用 token 认证）
        :param headers: 请求头
        :param http_log_debug: 是否开启调试模式
        :param timeout: 请求超时时间
        :param insecure: 是否跳过 SSL 验证
        :param cacert: CA 证书路径
        :param timings: 是否记录请求时间
        :param api_version: API 版本
        :param return_response: 是否返回完整响应对象
        """
        self.api_version = api_version
        self.username = username
        self.password = password
        self.project = project
        self.baseurl = baseurl.rstrip('/')
        # Has no protocol, use http
        if not urlparse(baseurl).scheme:
            self.baseurl = 'http://' + baseurl
        self.token = token
        self.http_log_debug = http_log_debug
        self.sid = ''
        self.sid_old = 'beegosessionID'
        self.sid_new = 'sid'
        self.session_id = None
        self.headers = headers if headers else {}
        parsed_url = urlparse(self.baseurl)
        self.protocol = parsed_url.scheme
        self.host = parsed_url.hostname
        self.port = parsed_url.port
        if timeout is not None:
            self.timeout = float(timeout)
        else:
            self.timeout = None
        # https
        if insecure:
            self.verify_cert = False
        else:
            if cacert:
                self.verify_cert = cacert
            else:
                self.verify_cert = True
        self.cacert = cacert
        self.timings = timings
        self.times = []  # [("item", starttime, endtime), ...]

        if self.token:
            self.headers["Authorization"] = "Bearer %s" % self.token
        elif self.username and self.password:
            auth_str = "%s %s" % (self.username, self.password)
            self.headers["Authorization"] = (
                    "Basic " + base64.b64encode(auth_str.encode()).decode()
            )
        self.return_response = return_response
        # 初始化日志记录器
        self._logger = logging.getLogger(__name__)
        if self.http_log_debug and not self._logger.handlers:
            # Logging level is already set on the root logger
            ch = logging.StreamHandler()
            self._logger.addHandler(ch)
            self._logger.propagate = False
            if hasattr(requests, 'logging'):
                rql = requests.logging.getLogger(requests.__name__)
                rql.addHandler(ch)
                rql.setLevel(logging.WARNING)

    def set_token(self, token):
        """设置 Bearer token"""
        self.token = token
        self.headers["Authorization"] = "Bearer %s" % self.token

    def http_log_req(self, method, url, kwargs):
        if not self.http_log_debug:
            return

        string_parts = ['curl -g -i']

        if self.verify_cert is not None:
            if not self.verify_cert:
                string_parts.append(' --insecure')

        string_parts.append(" '%s'" % url)
        string_parts.append(' -X %s' % method)

        headers = copy.deepcopy(kwargs['headers'])
        # because dict ordering changes from 2 to 3
        keys = sorted(headers.keys())
        for name in keys:
            value = headers[name]
            header = ' -H "%s: %s"' % (name, value)
            string_parts.append(header)
        cookies = kwargs['cookies'] if 'cookies' in kwargs else {}
        for name in sorted(cookies.keys()):
            value = cookies[name]
            cookie = header = ' -b "%s: %s"' % (name, value)
            string_parts.append(cookie)
        if 'data' in kwargs:
            data = json.loads(kwargs['data'])
            string_parts.append(" -d '%s'" % json.dumps(data))
        self._logger.debug("REQ: %s" % "".join(string_parts))

    def http_log_resp(self, resp):
        if not self.http_log_debug:
            return
        if resp.text and resp.status_code != 400:
            try:
                body = json.loads(resp.text)
            except ValueError:
                body = None
        else:
            body = None
        self._logger.debug("RESP: [%(status)s] %(headers)s\nRESP BODY: %(text)s\n",
                           {'status': resp.status_code, 'headers': resp.headers, 'text': json.dumps(body)})

    def request(self, url, method, return_response=False, **kwargs):
        kwargs.setdefault('headers', kwargs.get('headers', {}))
        kwargs['headers']['User-Agent'] = self.USER_AGENT
        kwargs['headers']['Accept'] = 'application/json'
        if 'body' in kwargs:
            kwargs['headers']['Content-Type'] = 'application/json'
            kwargs['data'] = json.dumps(kwargs['body'])
            del kwargs['body']
        if self.timeout is not None:
            kwargs.setdefault('timeout', self.timeout)

        self.http_log_req(method, url, kwargs)
        resp = requests.request(method, url, verify=self.verify_cert, **kwargs)
        self.http_log_resp(resp)
        # print(resp)
        if resp.text:
            try:
                body = json.loads(resp.text)
            except ValueError:
                pass
                body = None
        else:
            body = None
        if resp.status_code >= 400:
            raise exceptions.from_response(resp, resp.text, url, method)
        if return_response:
            return resp  # Return full response when requested
        return body

    def unauthenticate(self):
        """Forget all of our authentication information."""
        requests.get(
            '%s://%s/logout' % (self.protocol, self.host),
            cookies={self.sid: self.session_id},
            verify=self.verify_cert)
        logging.debug("Successfully logout")

    def get_timings(self):
        return self.times

    def reset_timings(self):
        self.times = []

    def _time_request(self, url, method, **kwargs):
        with utils.record_time(self.times, self.timings, method, url):
            body = self.request(url, method, **kwargs)
        return body

    @staticmethod
    def concat_url(endpoint, url):
        """Concatenate endpoint and final URL.

        E.g., "http://keystone/v2.0/" and "/tokens" are concatenated to
        "http://keystone/v2.0/tokens".

        :param endpoint: the base URL
        :param url: the final URL
        """
        return "%s/%s" % (endpoint.rstrip("/"), url.strip("/"))

    def _cs_request(self, url, method, **kwargs):
        if self.username and self.password and not self.session_id:
            self.authenticate()
        # build absolute URL
        url = self.concat_url(self.baseurl, url)
        # print(url)
        try:
            # Add session cookie only if we obtained one
            if self.session_id:
                kwargs.setdefault('cookies', {})[self.sid] = self.session_id

            body = self._time_request(url, method, **kwargs)
            return body
        except exceptions.Unauthorized as e:
            try:
                # first discard auth token, to avoid the possibly expired
                # token being re-used in the re-authentication attempt
                self.unauthenticate()
                # overwrite bad token
                self.authenticate()
                body = self._time_request(url, method, **kwargs)
                return body
            except exceptions.Unauthorized:
                raise e

    def get(self, url, **kwargs):
        # print("get fun")
        return self._cs_request(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        # print("post fun")
        return self._cs_request(url, 'POST', **kwargs)

    def put(self, url, **kwargs):
        # print("put fun")
        return self._cs_request(url, 'PUT', **kwargs)

    def delete(self, url, **kwargs):
        return self._cs_request(url, 'DELETE', **kwargs)

    def authenticate(self):
        if not self.baseurl:
            msg = ("Authentication requires 'baseurl', which should be specified in '%s'") % self.__class__.__name__
            raise exceptions.AuthorizationFailure(msg)

        if not self.username:
            msg = ("Authentication requires 'username', which should be specified in '%s'") % self.__class__.__name__
            raise exceptions.AuthorizationFailure(msg)

        if not self.password:
            msg = ("Authentication requires 'password', which should be specified in '%s'") % self.__class__.__name__
            raise exceptions.AuthorizationFailure(msg)

        try:
            resp = requests.post(
                self.baseurl + "/c/login",
                data={'principal': self.username, 'password': self.password},
                verify=self.verify_cert)
        except requests.exceptions.SSLError:
            msg = ("Certificate verify failed, please use '--os-cacert' option"
                   " to specify a CA bundle file to use in verifying a TLS"
                   " (https) server certificate or use '--insecure' option"
                   " to explicitly allow client to perform insecure"
                   " TLS (https) requests.")
            raise exceptions.AuthorizationFailure(msg)
        if resp.status_code == 200:
            self.session_id = resp.cookies.get(self.sid_old)
            self.sid = self.sid_old
            if not self.session_id:
                logging.debug("On newer version, cookie name is sid")
                self.session_id = resp.cookies.get(self.sid_new)
                self.sid = self.sid_new
            if not self.session_id:
                reason = "Tried cookie with names '%s' and '%s' and still no luck" % (
                    self.sid_old, self.sid_new)
                raise exceptions.AuthorizationFailure(reason)
            logging.debug("Successfully login, session id: %s" % self.session_id)
        if resp.status_code >= 400:
            msg = resp.text or ("The request you have made requires authentication. (HTTP 401)")
            reason = '{"reason": "%s", "message": "%s"}' % (resp.reason, msg)
            raise exceptions.AuthorizationFailure(reason)


def _construct_http_client(
        username, password, project, baseurl, token=None,
        headers=None, http_log_debug=False, timeout=None, insecure=False,
        cacert=None, timings=False, api_version=None, return_response=False, **kwargs):
    """
        Construct an HTTP client.
    """
    return HTTPClient(
        username, password, project, baseurl,
        token=token, headers=headers, http_log_debug=http_log_debug, timeout=timeout,
        insecure=insecure, cacert=cacert, timings=timings, api_version=api_version, return_response=return_response
    )
