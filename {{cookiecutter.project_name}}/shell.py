#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
from .util import args
from .exc import CommandError

class shellmain(object):
    def __init__(self, command_name, package_name, api_version):
        self.command_name = command_name
        self.package_name = package_name
        self.api_version = api_version

    def get_base_parse(self):
        parser = argparse.ArgumentParser(
            prog=self.command_name,
            description='',
            epilog='see {} command for help'.format(self.command_name),
            add_help=False
        )

        parser.add_argument('-v','--version',
                            action='version',
                            version='0.1'
                            )
        parser.add_argument('-h','--help',
                            help="command {} for help".format(self.command_name))

        return parser

    def import_modules(self, path):
        __import__(path)
        modules = sys.modules[path]
        return modules

    def get_subcommand_parser(self):
        parser = self.get_base_parse()
        subparser= parser.add_subparsers(metavar='<command>')
        module_path = '{}.{}.meters'.format(self.package_name, self.api_version)
        sub_modules = self.import_modules(module_path)
        for fn_name in (func for func in dir(sub_modules) if func.startswith('do_')):
            command = fn_name[3:].replace('_','-')
            callback = getattr(sub_modules,fn_name)
            desc=callback.__doc__ or ''
            help=desc.strip()
            arguments = getattr(callback,'arguments',[])
            subparser_s = subparser.add_parser(
                                             command,
                                             description=desc,
                                             add_help=False
                                            )
            for (args,kwargs) in arguments:
                subparser_s.add_argument(*args, **kwargs)
            subparser_s.set_defaults(func=callback)
        return parser

    def parse_args(self,argv):
        parser = self.get_base_parse()
        (option,args) = parser.parse_known_args(argv)
        subcommand_parser= self.get_subcommand_parser()
        return subcommand_parser.parse_args(argv)


    @args('command', metavar='<subcommand>', nargs='?',
          help='Display help for <subcommand>')
    def do_help(self, args):
        """Display help about this program or one of its subcommands."""
        if getattr(args, 'command', None):
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise CommandError("'%s' is not a valid subcommand" %
                                   args.command)
        else:
            self.parser.print_help()

    def main(self,argv):
        parsed = self.parse_args(argv)
        parsed.func(parsed)


def main(argv=None):
    if argv:
        argv = sys.argv[1:]

    shell = shellmain(
        command_name='{{cookiecutter.command_name}}',
        package_name='{{cookiecutter.package_name}}',
        api_version='{{cookiecutter.api_version}}'
    )
    shell.main(argv)
