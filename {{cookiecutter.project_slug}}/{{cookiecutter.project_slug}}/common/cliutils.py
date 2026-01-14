#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import getpass
import inspect
import os
import sys
import textwrap
import json

import prettytable
import six
from six import moves

from {{cookiecutter.project_slug}}.common import exceptions
from {{cookiecutter.project_slug}}.common import strutils
from {{cookiecutter.project_slug}}.common import uuidutils


def validate_args(fn, *args, **kwargs):
    """Check that the supplied args are sufficient for calling a function.

    >>> validate_args(lambda a: None)
    Traceback (most recent call last):
        ...
    MissingArgs: Missing argument(s): a
    >>> validate_args(lambda a, b, c, d: None, 0, c=1)
    Traceback (most recent call last):
        ...
    MissingArgs: Missing argument(s): b, d

    :param fn: the function to check
    :param arg: the positional arguments supplied
    :param kwargs: the keyword arguments supplied
    """
    argspec = inspect.signature(fn)

    num_defaults = len(argspec.defaults or [])
    required_args = argspec.args[:len(argspec.args) - num_defaults]

    def isbound(method):
        return getattr(method, '__self__', None) is not None

    if isbound(fn):
        required_args.pop(0)

    missing = [arg for arg in required_args if arg not in kwargs]
    missing = missing[len(args):]
    if missing:
        raise exceptions.MissingArgs(missing)


def arg(*args, **kwargs):
    """Decorator for CLI args.

    Example:

    >>> @arg("name", help="Name of the new entity")
    ... def entity_create(args):
    ...     pass
    """

    def _decorator(func):
        if 'help' in kwargs:
            required = kwargs.get('required', False)
            if required:
                kwargs['help'] += ' Required.'
        func.__dict__.setdefault('arguments', []).insert(0, (args, kwargs))
        return func

    return _decorator


def env(*args, **kwargs):
    """Returns the first environment variable set.

    If all are empty, defaults to '' or keyword arg `default`.
    """
    for arg in args:
        value = os.environ.get(arg)
        if value:
            return value
    return kwargs.get('default', '')


def add_arg(func, *args, **kwargs):
    """Bind CLI arguments to a shell.py `do_foo` function."""

    if not hasattr(func, 'arguments'):
        func.arguments = []

    # NOTE(sirp): avoid dups that can occur when the module is shared across
    # tests.
    if (args, kwargs) not in func.arguments:
        # Because of the semantics of decorator composition if we just append
        # to the options list positional options will appear to be backwards.
        func.arguments.insert(0, (args, kwargs))


def unauthenticated(func):
    """Adds 'unauthenticated' attribute to decorated function.

    Usage:

    >>> @unauthenticated
    ... def mymethod(f):
    ...     pass
    """
    func.unauthenticated = True
    return func


def isunauthenticated(func):
    """Checks if the function does not require authentication.

    Mark such functions with the `@unauthenticated` decorator.

    :returns: bool
    """
    return getattr(func, 'unauthenticated', False)


def pretty_choice_list(l):
    return ', '.join("'%s'" % i for i in l)


def _print(pt, order):
    if sys.version_info >= (3, 0):
        print(pt.get_string(sortby=order))
    else:
        print(strutils.safe_encode(pt.get_string(sortby=order)))


def print_list(objs, fields, formatters={}, order_by=None, align='l'):
    """
    Print a list of objects as a table.
    """
    mixed_case_fields = ['serverId']
    pt = prettytable.PrettyTable([f for f in fields], caching=False)
    pt.aligns = [align for f in fields]

    for o in objs:
        row = []
        for field in fields:
            if field in formatters:
                row.append(formatters[field](o))
            else:
                if field in mixed_case_fields:
                    field_name = field.replace(' ', '_')
                else:
                    field_name = field.lower().replace(' ', '_')
                if type(o) == dict and field in o:
                    data = o[field]
                else:
                    data = getattr(o, field_name, '')
                row.append(data)
        pt.add_row(row)

    if order_by is None:
        order_by = fields[0]
    _print(pt, order_by)


def print_dict(d, property="Property", value="Value"):
    """
    Print a dictionary as a table.
    """
    pt = prettytable.PrettyTable([property, value], caching=False)
    pt.aligns = ['l', 'l']
    [pt.add_row(list(r)) for r in six.iteritems(d)]
    _print(pt, property)


def get_password(max_password_prompts=3):
    """Read password from TTY."""
    verify = strutils.bool_from_string(env("OS_VERIFY_PASSWORD"))
    pw = None
    if hasattr(sys.stdin, "isatty") and sys.stdin.isatty():
        # Check for Ctrl-D
        try:
            for __ in moves.range(max_password_prompts):
                pw1 = getpass.getpass("OS Password: ")
                if verify:
                    pw2 = getpass.getpass("Please verify: ")
                else:
                    pw2 = pw1
                if pw1 == pw2 and pw1:
                    pw = pw1
                    break
        except EOFError:
            pass
    return pw


def find_resource(manager, name_or_id, **find_args):
    """Look for resource in a given manager.

    Used as a helper for the _find_* methods.
    Example:

    .. code-block:: python

        def _find_hypervisor(cs, hypervisor):
            #Get a hypervisor by name or ID.
            return cliutils.find_resource(cs.hypervisors, hypervisor)
    """
    # first try to get entity as integer id
    try:
        return manager.get(int(name_or_id))
    except (TypeError, ValueError, exceptions.NotFound):
        pass

    # now try to get entity as uuid
    try:
        if six.PY2:
            tmp_id = strutils.safe_encode(name_or_id)
        else:
            tmp_id = strutils.safe_decode(name_or_id)

        if uuidutils.is_uuid_like(tmp_id):
            return manager.get(tmp_id)
    except (TypeError, ValueError, exceptions.NotFound):
        pass

    # for str id which is not uuid
    if getattr(manager, 'is_alphanum_id_allowed', False):
        try:
            return manager.get(name_or_id)
        except exceptions.NotFound:
            pass

    try:
        try:
            return manager.find(human_id=name_or_id, **find_args)
        except exceptions.NotFound:
            pass

        # finally try to find entity by name
        try:
            resource = getattr(manager, 'resource_class', None)
            name_attr = resource.NAME_ATTR if resource else 'name'
            kwargs = {name_attr: name_or_id}
            kwargs.update(find_args)
            return manager.find(**kwargs)
        except exceptions.NotFound:
            msg = ("No %(name)s with a name or "
                   "ID of '%(name_or_id)s' exists.") % \
                  {
                      "name": manager.resource_class.__name__.lower(),
                      "name_or_id": name_or_id
                  }
            raise exceptions.CommandError(msg)
    except exceptions.NoUniqueMatch:
        msg = ("Multiple %(name)s matches found for "
               "'%(name_or_id)s', use an ID to be more specific.") % \
              {
                  "name": manager.resource_class.__name__.lower(),
                  "name_or_id": name_or_id
              }
        raise exceptions.CommandError(msg)


def exit(msg=''):
    if msg:
        print(msg, file=sys.stderr)
    sys.exit(1)
