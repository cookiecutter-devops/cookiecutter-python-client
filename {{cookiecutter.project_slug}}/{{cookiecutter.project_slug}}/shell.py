#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import argparse
import importlib
import logging
import utils
import exc

logger = logging.getLogger(__name__)


class HelpAction(argparse._HelpAction):
    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()
        sys.exit(0)


class shellmain(object):
    def __init__(self, command_name, package_name, api_version):
        self.command_name = command_name
        self.package_name = package_name
        self.api_version = api_version
        self.subcommands = {}

    def get_base_parse(self):
        parser = argparse.ArgumentParser(
            prog=self.command_name,
            description="",
            epilog="see {} command for help".format(self.command_name),
            add_help=False,
        )

        parser.add_argument("-v", "--version", action="version", version="0.1")
        parser.add_argument(
            "-h",
            "--help",
            action=HelpAction,
            help="Show this help message and exit",
        )

        parser.add_argument(
            "--debug",
            default=False,
            action="store_true",
            help="Defaults to env[%(env)s]." % {"env": "DEBUG"},
        )

        return parser

    def import_modules(self, path):
        __import__(path)
        modules = sys.modules[path]
        return modules

    def _find_actions(self, subparser, sub_module):
        """Find and register actions from a given module."""
        for fn_name in (
            func for func in dir(sub_module) if func.startswith("do_")
        ):
            command = fn_name[3:].replace("_", "-")
            callback = getattr(sub_module, fn_name)
            desc = callback.__doc__ or ""
            help_text = desc.strip()
            arguments = getattr(callback, "arguments", [])

            subparser_instance = subparser.add_parser(
                command, description=desc, help=help_text, add_help=False
            )

            # Add custom help action
            subparser_instance.add_argument(
                "-h",
                "--help",
                action=HelpAction,
                help="Show this help message and exit",
            )

            for args_tuple, kwargs in arguments:
                subparser_instance.add_argument(*args_tuple, **kwargs)

            subparser_instance.set_defaults(func=callback)
            self.subcommands[command] = subparser_instance

    def get_subcommand_parser(self):
        parser = self.get_base_parse()
        subparsers = parser.add_subparsers(dest="command", metavar="<command>")
        subparsers.required = True

        # Get the path to the api_version directory
        api_module_path = "{}.{}".format(self.package_name, self.api_version)
        api_module = importlib.import_module(api_module_path)
        api_dir = os.path.dirname(api_module.__file__)

        # Iterate through all .py files in the api_version directory
        for filename in os.listdir(api_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                # Get the module name without the .py extension
                module_name = filename[:-3]
                # Import the module
                module_path = "{}.{}".format(api_module_path, module_name)
                sub_module = self.import_modules(module_path)

                # Process all do_* functions in the module using _find_actions
                self._find_actions(subparsers, sub_module)

        return parser

    def parse_args(self, argv):
        subcommand_parser = self.get_subcommand_parser()
        return subcommand_parser.parse_args(argv)

    @utils.args(
        "command",
        metavar="<subcommand>",
        nargs="?",
        help="Display help for <subcommand>",
    )
    def do_help(self, args):
        """Display help about this program or one of its subcommands."""
        if getattr(args, "command", None):
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise exc.CommandError(
                    "'%s' is not a valid subcommand" % args.command
                )
        else:
            self.parser.print_help()

    def setup_debugging(self, debug):
        if not debug:
            return

        streamhandler = logging.StreamHandler()
        streamformat = "%(levelname)s (%(module)s:%(lineno)d) %(message)s"
        streamhandler.setFormatter(logging.Formatter(streamformat))
        logger.setLevel(logging.DEBUG)
        logger.addHandler(streamhandler)

    def main(self, argv):
        if argv is None:
            argv = sys.argv[1:]

        # 获取子命令解析器并构建子命令
        parser = self.get_subcommand_parser()

        try:
            parsed = parser.parse_args(argv)
        except argparse.ArgumentError as e:
            # 尝试确定是否提供了子命令
            if argv:
                subcommand = argv[0]
                if subcommand in self.subcommands:
                    # 显示特定子命令的帮助
                    self.subcommands[subcommand].print_help()
                    sys.exit(2)
            # 如果没有子命令或子命令未找到，显示通用帮助
            parser.print_help()
            print(f"Error: {e}")
            sys.exit(2)

        # 设置调试模式
        self.setup_debugging(
            parsed.debug if hasattr(parsed, "debug") else False
        )

        if not hasattr(parsed, "func"):
            parser.print_help()
            sys.exit(2)

        # 调用子命令函数
        try:
            parsed.func(parsed)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    shell = shellmain(
        command_name="{{cookiecutter.command_name}}",
        package_name="{{cookiecutter.package_name}}",
        api_version="{{cookiecutter.api_version}}",
    )
    shell.main(argv)
