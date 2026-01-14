#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from {{cookiecutter.project_slug}} import base
from {{cookiecutter.project_slug}}.common import importutils


class Extension(base.HookableMixin):
    """Extension descriptor."""

    SUPPORTED_HOOKS = ('__pre_parse_args__', '__post_parse_args__')

    def __init__(self, name, module):
        self.name = name
        self.module = module
        self._parse_extension_module()

    def _parse_extension_module(self):
        self.manager_class = None
        for attr_name, attr_value in self.module.__dict__.items():
            if attr_name in self.SUPPORTED_HOOKS:
                self.add_hook(attr_name, attr_value)
            elif importutils.safe_issubclass(attr_value, base.Manager):
                self.manager_class = attr_value

    def __repr__(self):
        return "<Extension '%s'>" % self.name
