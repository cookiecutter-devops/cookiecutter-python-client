#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import contextlib
import time
import prettytable
import six


def env(*args, **kwargs):
    """Returns the first environment variable set.

    If all are empty, defaults to '' or keyword arg `default`.
    """
    for arg in args:
        value = os.environ.get(arg)
        if value:
            return value
    return kwargs.get("default", "")


def args(*args, **kwargs):
    """Decorator for CLI args.

    Example:

    >>> @arg("name", help="Name of the new entity")
    ... def entity_create(args):
    ...     pass
    """

    def _decorator(func):
        if "help" in kwargs:
            required = kwargs.get("required", False)
            if required:
                kwargs["help"] += " Required."
        func.__dict__.setdefault("arguments", []).insert(0, (args, kwargs))
        return func

    return _decorator


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


def safe_decode(text, incoming=None, errors="strict"):
    if not isinstance(text, (six.string_types, six.binary_type)):
        raise TypeError("%s can't be decoded" % type(text))

    if isinstance(text, six.text_type):
        return text

    if not incoming:
        incoming = sys.stdin.encoding or sys.getdefaultencoding()

    try:
        return text.decode(incoming, errors)
    except UnicodeDecodeError:
        return text.decode("utf-8", errors)


def safe_encode(text, incoming=None, encoding="utf-8", errors="strict"):
    if not isinstance(text, (six.string_types, six.binary_type)):
        raise TypeError("%s can't be encoded" % type(text))

    if not incoming:
        incoming = sys.stdin.encoding or sys.getdefaultencoding()

    if isinstance(text, six.text_type):
        if six.PY3:
            return text.encode(encoding, errors).decode(incoming)
        else:
            return text.encode(encoding, errors)
    elif text and encoding != incoming:
        # Decode text before encoding it with `encoding`
        text = safe_decode(text, incoming, errors)
        if six.PY3:
            return text.encode(encoding, errors).decode(incoming)
        else:
            return text.encode(encoding, errors)

    return text


def pretty_choice_list(l):
    return ", ".join("'%s'" % i for i in l)


def print_list(objs, fields, formatters=None, field_settings=None):
    formatters = formatters or {}
    field_settings = field_settings or {}
    pt = prettytable.PrettyTable([f for f in fields], caching=False)
    pt.align = "l"

    for o in objs:
        row = []
        for field in fields:
            if field in field_settings:
                for setting, value in six.iteritems(field_settings[field]):
                    setting_dict = getattr(pt, setting)
                    setting_dict[field] = value

            if field in formatters:
                row.append(formatters[field](o))
            else:
                field_name = field.lower().replace(" ", "_")
                data = getattr(o, field_name, None) or ""
                row.append(data)
        pt.add_row(row)

    print(safe_encode(pt.get_string()))


def print_dict(d, property="Property", max_column_width=80, headers=None):
    if headers is None:
        headers = [property, "Value"]
    pt = prettytable.PrettyTable(headers, caching=False)
    pt.aligns = ["l", "l"]
    pt.max_width = max_column_width
    [pt.add_row(list(r)) for r in d.items()]
    print(safe_encode(pt.get_string(sortby=property)))


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
