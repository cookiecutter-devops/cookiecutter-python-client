#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import itertools
import os
import glob
import importlib
import argparse
import sys
import pkgutil
import {{cookiecutter.project_slug}}
import logging
from {{cookiecutter.project_slug}} import client
from {{cookiecutter.project_slug}} import extension
from {{cookiecutter.project_slug}}.common import cliutils
from {{cookiecutter.project_slug}}.common import exceptions as exc
from {{cookiecutter.project_slug}}.common import importutils
from {{cookiecutter.project_slug}}.common import strutils

DEFAULT_API_VERSION = "{{cookiecutter.api_version}}".strip("v")

logger = logging.getLogger(__name__)


class HelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(HelpFormatter, self).start_section(heading)


class ClientArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(ClientArgumentParser, self).__init__(*args, **kwargs)

    def error(self, message):
        """error(message: string)

        Prints a usage message incorporating the message to stderr and
        exits.
        """
        self.print_usage(sys.stderr)
        choose_from = ' (choose from'
        progparts = self.prog.partition(' ')
        self.exit(2,
                  ("error: %(errmsg)s\nTry '%(mainp)s help %(subp)s'"
                   " for more information.\n") % {
                      'errmsg': message.split(choose_from)[0],
                      'mainp': progparts[0],
                      'subp': progparts[2]})

    def _get_option_tuples(self, option_string):
        """returns (action, option, value) candidates for an option prefix

        Returns [first candidate] if all candidates refers to current and
        deprecated forms of the same options parsing succeed.
        """
        option_tuples = (super(ClientArgumentParser, self)._get_option_tuples(option_string))
        if len(option_tuples) > 1:
            normalizeds = [
                option.replace('_', '-')
                for action, option, value in option_tuples
            ]
            if len(set(normalizeds)) == 1:
                return option_tuples[:1]
        return option_tuples


class Shellmain(object):
    times = []

    def _append_global_identity_args(self, parser, argv):
        # Register the CLI arguments that have moved to the session object.
        parser.set_defaults(os_username=cliutils.env('OS_USERNAME'))
        parser.set_defaults(os_password=cliutils.env('OS_PASSWORD'))
        parser.set_defaults(os_project=cliutils.env('OS_PROJECT'))
        parser.set_defaults(os_baseurl=cliutils.env('OS_BASEURL'))

    def get_base_parser(self, argv):
        parser = ClientArgumentParser(
            prog='{{cookiecutter.project_slug}}',
            description=__doc__.strip() if __doc__ else "{{cookiecutter.project_slug}} shell",
            epilog='Run "{{cookiecutter.command_name}} help SUBCOMMAND" for help on a subcommand.',
            add_help=False,
            formatter_class=HelpFormatter,
        )
        # Global arguments
        parser.add_argument(
            '-h',
            '--help',
            action='store_true',
            help=argparse.SUPPRESS, )

        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help="Print debugging output.")

        parser.add_argument(
            '--timings',
            default=False,
            action='store_true',
            help="Print call timing info.")

        parser.add_argument(
            '--version', action='version', version={{cookiecutter.project_slug}}.__version__)

        parser.add_argument(
            '--os-username',
            dest='os_username',
            metavar='<username>',
            default=cliutils.env('OS_USERNAME'),
            help='Username, defaults to env[OS_USERNAME].')

        parser.add_argument(
            '--os-password',
            dest='os_password',
            metavar='<password>',
            default=cliutils.env('OS_PASSWORD'),
            help="User's password, defaults to env[OS_PASSWORD].")

        parser.add_argument(
            '--os-project',
            dest='os_project',
            metavar='<project>',
            default=cliutils.env('OS_PROJECT'),
            help="Project Id, defaults to env[OS_PROJECT].")

        parser.add_argument(
            '--timeout',
            metavar='<timeout>',
            help="Set request timeout (in seconds).")

        parser.add_argument(
            '--os-baseurl',
            metavar='<baseurl>',
            default=cliutils.env('OS_BASEURL'),
            help='API base url, defaults to env[OS_BASEURL].')
        parser.add_argument(
            '--token',
            dest='token',
            metavar='<token>',
            default=cliutils.env('OS_TOKEN'),
            help="Token for authentication, defaults to env[OS_TOKEN].")

        parser.add_argument(
            '--insecure',
            default=False,
            action='store_true',
            dest='insecure',
            help='Explicitly allow client to perform '
                 '"insecure" TLS (https) requests. The '
                 'server\'s certificate will not be verified '
                 'against any certificate authorities. This '
                 'option should be used with caution.')

        parser.add_argument(
            '--os-cacert',
            dest='os_cacert',
            metavar='<ca-certificate>',
            default=os.environ.get('OS_CACERT'),
            help='Specify a CA bundle file to use in '
                 'verifying a TLS (https) server certificate. '
                 'Defaults to env[OS_CACERT].')

        parser.add_argument(
            '--os-api-version',
            metavar='<api-version>',
            default=cliutils.env(
                'API_VERSION', default=DEFAULT_API_VERSION),
            help=('Accepts X, X.Y (where X is major and Y is minor part) or '
                  '"X.latest", defaults to env[API_VERSION].'))

        self._append_global_identity_args(parser, argv)

        return parser

    def _find_actions(self, subparsers, actions_module, version, do_help):
        for attr in (a for a in dir(actions_module) if a.startswith('do_')):
            # I prefer to be hypen-separated instead of underscores.
            command = attr[3:].replace('_', '-')
            callback = getattr(actions_module, attr)
            desc = callback.__doc__ or ''
            help = desc.strip().split('\n')[0]
            arguments = getattr(callback, 'arguments', [])

            subparser = subparsers.add_parser(command,
                                              help=help,
                                              description=desc,
                                              add_help=False,
                                              formatter_class=HelpFormatter
                                              )
            subparser.add_argument('-h', '--help',
                                   action='help',
                                   help=argparse.SUPPRESS,
                                   )
            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)
            # Store version and do_help information if needed for future use
            subparser.set_defaults(version=version, do_help=do_help)

    def get_subcommand_parser(self, version, do_help=False, argv=None):
        parser = self.get_base_parser(argv)

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')
        actions_module = importutils.import_versioned_module(version, 'shell')
        self._find_actions(subparsers, actions_module, version, do_help)
        self._find_actions(subparsers, self, version, do_help)
        # Add any extensions' actions
        for extension in self.extensions:
            self._find_actions(subparsers, extension.module, version, do_help)

        # Add bash-completion subparser
        self._add_bash_completion_subparser(subparsers)

        return parser

    def do_bash_completion(self, _args):
        """Prints arguments for bash-completion.

        Prints all of the commands and options to stdout so that the
        venus.bash_completion script doesn't have to hard code them.
        """
        commands = set()
        options = set()
        for sc_str, sc in self.subcommands.items():
            commands.add(sc_str)
            for option in sc._optionals._option_string_actions.keys():
                options.add(option)

        commands.remove('bash-completion')
        commands.remove('bash_completion')
        print(' '.join(commands | options))

    def _add_bash_completion_subparser(self, subparsers):
        subparser = subparsers.add_parser(
            'bash_completion',
            add_help=False,
            formatter_class=HelpFormatter)
        self.subcommands['bash_completion'] = subparser
        subparser.set_defaults(func=self.do_bash_completion)

    @cliutils.arg(
        'command',
        metavar='<subcommand>',
        nargs='?',
        help='Display help for <subcommand>.')
    def do_help(self, args):
        """Display help about this program or one of its subcommands."""
        if args.command:
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise exc.CommandError(
                    ("'%s' is not a valid subcommand") % args.command)
        else:
            self.parser.print_help()

    def setup_debugging(self, debug):
        if not debug:
            return
        streamformat = "%(levelname)s (%(module)s:%(lineno)d) %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=streamformat)
        logging.getLogger('iso8601').setLevel(logging.WARNING)

    def _dump_timings(self, timings):
        results = [{
            "url": url,
            "seconds": end - start
        } for url, start, end in timings]
        total = 0.0
        for tyme in results:
            total += tyme['seconds']

        results.append({"url": "Total", "seconds": total})
        # print(results)
        cliutils.print_list(results, ['url', 'seconds'], align='c')
        print("Total: %s seconds" % total)

    def _discover_via_python_path(self, version):
        # 查找了以 python_{{cookiecutter.project_slug}}_ext 来结尾的 python 模块
        for (module_loader, name, ispkg) in pkgutil.iter_modules():
            if name.endswith('python_{{cookiecutter.project_slug}}_ext'):
                if not hasattr(module_loader, 'load_module'):
                    module_loader = module_loader.find_module(name)
                module = module_loader.load_module(name)
                yield name, module

    def _discover_via_contrib_path(self, version):
        # 查找了位于 {{cookiecutter.project_slug}}/v2/contrib 下的除 __init__.py 之外的所有py文件
        module_path = os.path.dirname(os.path.abspath(__file__))
        version_str = "v%s" % version.replace('.', '_')
        ext_path = os.path.join(module_path, version_str, 'contrib')
        ext_glob = os.path.join(ext_path, "*.py")

        for ext_path in glob.iglob(ext_glob):
            name = os.path.basename(ext_path)[:-3]

            if name == "__init__":
                continue
            module_name = "{{cookiecutter.project_slug}}.{}.contrib.{}".format(version_str, name)
            try:
                module = importlib.import_module(module_name)
                yield name, module
            except ImportError as e:
                logger.warning("Failed to import extension %s: %s", module_name, e)

    def _discover_extensions(self, version):
        extensions = []
        for name, module in itertools.chain(
                self._discover_via_python_path(version),
                self._discover_via_contrib_path(version)):
            extension = {{cookiecutter.project_slug}}.extension.Extension(name, module)
            extensions.append(extension)

        return extensions

    def _run_extension_hooks(self, hook_type, *args, **kwargs):
        """
        Run hooks for all registered extensions.
        _run_extension_hooks函数则对扫描到的extensions做遍历，并运行带有pre_parse_args的钩子
        """
        for extension in self.extensions:
            extension.run_hooks(hook_type, *args, **kwargs)

    def main(self, argv):
        base_argv = copy.deepcopy(argv)
        parser = self.get_base_parser(base_argv)
        (args, args_list) = parser.parse_known_args(base_argv)
        self.setup_debugging(args.debug)
        do_help = ('help' in argv) or ('--help' in argv) or (
                '-h' in argv) or not argv

        if not args.os_api_version:
            api_version = DEFAULT_API_VERSION
        else:
            api_version = args.os_api_version

        # build available subcommands based on version
        self.extensions = self._discover_extensions(api_version)
        self._run_extension_hooks('__pre_parse_args__')

        os_username = args.os_username
        os_password = args.os_password
        os_project = args.os_project
        os_baseurl = args.os_baseurl
        subcommand_parser = self.get_subcommand_parser(api_version, do_help=do_help, argv=argv)
        self.parser = subcommand_parser

        if args.help or not argv:
            subcommand_parser.print_help()
            return 0

        args = subcommand_parser.parse_args(argv)
        self._run_extension_hooks('__post_parse_args__', args)

        # Short-circuit and deal with help right away.
        if not hasattr(args, 'func') or args.func == self.do_help:
            self.do_help(args)
            return 0
        elif args.func == self.do_bash_completion:
            self.do_bash_completion(args)
            return 0

        insecure = args.insecure
        cacert = args.os_cacert
        if not os_baseurl:
            print(("ERROR (CommandError): You must provide harbor url via "
                   "either --os-baseurl or env[OS_BASEURL]."))
            return 1
        # print(api_version, os_username, os_password, os_project, os_baseurl)
        self.cs = client.Client(
            api_version,
            username=os_username,
            password=os_password,
            project=os_project,
            baseurl=os_baseurl,
            extensions=self.extensions,
            token=args.token,
            timings=args.timings,
            http_log_debug=args.debug,
            insecure=insecure,
            cacert=cacert,
            timeout=args.timeout
        )
        # 如果用户提供了用户名和密码，尝试认证
        if os_username and os_password:
            try:
                self.cs.authenticate()
            except exc.Unauthorized:
                raise exc.CommandError("Invalid Harbor credentials.")
            except exc.AuthorizationFailure as e:
                raise exc.CommandError("Unable to authorize user '%s': %s"
                                       % (os_username, e))
        # 调用子命令函数处理剩余参数
        args.func(self.cs, args)
        if args.timings:
            self._dump_timings(self.times + self.cs.get_timings())


def main():
    try:
        argv = [strutils.safe_decode(a) for a in sys.argv[1:]]
        Shellmain().main(argv)
    except KeyboardInterrupt:
        print("... terminating client", file=sys.stderr)
        sys.exit(130)
    except exc.CommandError as e:
        print("CommandError: %s" % e)
        sys.exit(127)


if __name__ == "__main__":
    main()
