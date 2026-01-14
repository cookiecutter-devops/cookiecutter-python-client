"""
Base utilities to build API operation managers and objects on top of.
"""


class HookableMixin(object):
    """Mixin so classes can register and run hooks."""
    _hooks_map = {}

    @classmethod
    def add_hook(cls, hook_type, hook_func):
        if hook_type not in cls._hooks_map:
            cls._hooks_map[hook_type] = []

        cls._hooks_map[hook_type].append(hook_func)

    @classmethod
    def run_hooks(cls, hook_type, *args, **kwargs):
        hook_funcs = cls._hooks_map.get(hook_type) or []
        for hook_func in hook_funcs:
            hook_func(*args, **kwargs)


class Manager(HookableMixin):
    """Manager for API service.

    Managers interact with a particular type of API (projects, users,
    reposiries,etc.) and provide CRUD operations for them.
    """

    def __init__(self, api):
        """Initialize a new manager with the provided API client.

        :param api: API client object
        """
        super(Manager, self).__init__()
        self.api = api

    @property
    def client(self):
        return self.api.client

    @property
    def api_version(self):
        return self.api.api_version

    def _head(self, url):
        resp = self.api.client.head(url)
        return resp.status_code == 204

    def _list(self, url, body=None):
        if body:
            data = self.api.client.post(url, body=body)
        else:
            data = self.api.client.get(url)
        return data

    def _get(self, url, return_response=False):
        return self.api.client.get(url, return_response=return_response)

    def _create(self, url, body=None, **kwargs):
        return self.api.client.post(url, body=body)

    def _delete(self, url):
        return self.api.client.delete(url)

    def _update(self, url, body, **kwargs):
        return self.api.client.put(url, body=body)
