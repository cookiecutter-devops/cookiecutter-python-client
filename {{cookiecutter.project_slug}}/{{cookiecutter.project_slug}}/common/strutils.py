#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
System-level utilities and helper functions.
"""

import logging
import sys
import six

LOG = logging.getLogger(__name__)


def int_from_bool_as_string(subject):
    """
    Interpret a string as a boolean and return either 1 or 0.

    Any string value in:

        ('True', 'true', 'On', 'on', '1')

    is interpreted as a boolean True.

    Useful for JSON-decoded stuff and config file parsing
    """
    return bool_from_string(subject) and 1 or 0


def bool_from_string(subject):
    """
    Interpret a string as a boolean.

    Any string value in:

        ('True', 'true', 'On', 'on', 'Yes', 'yes', '1')

    is interpreted as a boolean True.

    Useful for JSON-decoded stuff and config file parsing
    """
    if isinstance(subject, bool):
        return subject
    if isinstance(subject, six.string_types):
        if subject.strip().lower() in ('true', 'on', 'yes', '1'):
            return True
    return False


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
