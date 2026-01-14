#!/usr/bin/env python
# -*- coding: utf-8 -*-
import contextlib
import time
import six
import re


def make_size_human_readable(size):
    suffix = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB"]
    base = 1024.0
    index = 0

    if size is None:
        size = 0
    while size >= base:
        index = index + 1
        size = size / base

    padded = "%.1f" % size
    stripped = padded.rstrip("0").rstrip(".")

    return "%s%s" % (stripped, suffix[index])


@contextlib.contextmanager
def record_time(times, enabled, *args):
    """Record the time of a specific action.

    :param times: A list of tuples holds time data.
    :type times: list
    :param enabled: Whether timing is enabled.
    :type enabled: bool
    :param *args: Other data to be stored besides time data, these args
                  will be joined to a string.
    """
    if not enabled:
        yield
    else:
        start = time.time()
        yield
        end = time.time()
        times.append((" ".join(args), start, end))


def get_function_name(func):
    if six.PY2:
        if hasattr(func, "im_class"):
            return "%s.%s" % (func.im_class, func.__name__)
        else:
            return "%s.%s" % (func.__module__, func.__name__)
    else:
        return "%s.%s" % (func.__module__, func.__qualname__)


def strip_version(endpoint):
    """Strip version from the last component of endpoint if present."""
    # Get rid of trailing '/' if present
    if endpoint.endswith('/'):
        endpoint = endpoint[:-1]
    url_bits = endpoint.split('/')
    # regex to match 'v1' or 'v2.0' etc
    if re.match('v\d+\.?\d*', url_bits[-1]):
        endpoint = '/'.join(url_bits[:-1])
    return endpoint
