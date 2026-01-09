#!/usr/bin/env python
# -*- coding: utf-8 -*-


def args(*args,**kwargs):
    def _decorator(func):
        if 'help' in kwargs:
            required = kwargs.get('required', False)
            if required:
                kwargs['help'] += " Required."
        func.__dict__.setdefault("arguments",[]).insert(0,(args,kwargs))
        return func
    return _decorator
