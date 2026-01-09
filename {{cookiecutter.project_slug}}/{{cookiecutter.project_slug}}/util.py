#!/usr/bin/env python
# -*- coding: utf-8 -*-
import prettytable

def args(*args,**kwargs):
    def _decorator(func):
        if 'help' in kwargs:
            required = kwargs.get('required', False)
            if required:
                kwargs['help'] += " Required."
        func.__dict__.setdefault("arguments",[]).insert(0,(args,kwargs))
        return func
    return _decorator

def pretty_choice_list(l):
    return ', '.join("'%s'" % i for i in l)


def print_list(objs, fields, formatters={}):
    mixed_case_fields = ['serverId']
    pt = prettytable.PrettyTable([f for f in fields], caching=False)
    pt.aligns = ['l' for f in fields]

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
                data = getattr(o, field_name, '')
                row.append(data)
        pt.add_row(row)

    if len(objs) > 0:
        print(str(pt.get_string(sortby=fields[0])))


def print_dict(d, property="Property"):
    pt = prettytable.PrettyTable([property, 'Value'], caching=False)
    pt.aligns = ['l', 'l']
    [pt.add_row(list(r)) for r in d.items()]
    print(str(pt.get_string(sortby=property)))
