#!/usr/bin/env python
# -*- coding: utf-8 -*-
from {{cookiecutter.project_slug}} import base


class Controller(base.Manager):
    def __init__(self, client):
        super(Controller, self).__init__(client)

    def list(self, **kwargs):
        """List images."""
        return self._list("/v2/_catalog", **kwargs)

    def list_tags(self, image_name):
        """Get tags for an image."""
        return self._get("/v2/%s/tags/list" % image_name)
