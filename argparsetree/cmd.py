from __future__ import print_function

from argparse import ArgumentParser

import sys


class BaseCommand(object):
    """
    The base command object

    :var description: The brief description of the command
    :var sub_commands: A dictionary mapping names to sub commands. Each value should be a class
        inheriting from ``BaseCommand``. If not set the first sentence of the docstring is used.
    :var help: The full help text to display. If not set the docstring is used.
    :var arg_parse_class: The class to use as the root argument parser (should extend or implement ``argparse.ArgumanetParser``)
    """
    description = None
    help = None
    sub_commands = {}
    arg_parse_class = ArgumentParser

    def __init__(self, name=None, argv=None):
        """
        Creates the command
        :param name: The name the command is registered to
        :param argv: List of argument values. If ``None``, ``sys.argv[1:]`` is used.
        """
        self.name = name
        self._arg_parser = None
        self.argv = argv if argv is not None else sys.argv[1:]

    @property
    def sub_parser_dest_name(self):
        """
        The name of the argument the name of the sub command will be stored in
        """
        if self.name:
            return u'{0}__sub_command'.format(self.name)
        return 'sub_command'

    @property
    def arg_parser(self):
        if not self._arg_parser:
            self._arg_parser = self.get_root_argparser()
            self.add_args(self._arg_parser)
            self.register_sub_commands(self._arg_parser)

        return self._arg_parser

    def parse_args(self):
        """
        Parses the command line arguments

        :return: The arguments taken from the command line
        """
        return self.arg_parser.parse_args(self.argv)

    def add_args(self, parser):
        """
        Adds arguments to the argument parser. This is used to modify which arguments are processed by the command.

        For a full description of the argument parser see https://docs.python.org/3/library/argparse.html.

        :param parser: The argument parser object
        """
        pass

    def register_sub_commands(self, parser):
        """
        Add any sub commands to the argument parser.

        :param parser: The argument parser object
        """
        sub_commands = self.get_sub_commands()
        if sub_commands:
            sub_parsers = parser.add_subparsers(dest=self.sub_parser_dest_name)

            for name, cls in sub_commands.items():
                cmd = cls(name)

                sub_parser = sub_parsers.add_parser(name, help=cmd.get_description(), description=cmd.get_help())

                cmd.add_args(sub_parser)
                cmd.register_sub_commands(sub_parser)

    def get_root_argparser(self):
        """
        Gets the root argument parser object.
        """
        return self.arg_parse_class(self.get_description())

    def get_sub_commands(self):
        """
        Gets a dictionary mapping names to sub commands. Values should be classes inheriting from Base.

        :return: The list of sub commands.
        """
        return self.sub_commands

    def get_description(self):
        """
        Gets the description of the command. If its not supplied the first sentence of the doc string is used.
        """
        if self.description:
            return self.description
        elif self.__doc__ and self.__doc__.strip():
            return self.__doc__.strip().split('.')[0] + '.'
        else:
            return ''

    def get_help(self):
        """
        Gets the help text for the command. If its not supplied the doc string is used.
        """
        if self.help:
            return self.help
        elif self.__doc__ and self.__doc__.strip():
            return self.__doc__.strip()
        else:
            return ''

    def action(self, args):
        """
        Performs the action of the command.

        This should be implemented by sub classes.

        :param args: The arguments parsed from parse_args
        :return: The status code of the action (0 on success)
        """
        self.arg_parser.print_help()
        return 1

    def run(self, args=None):
        """
        Runs the command passing in the parsed arguments.

        :param args: The arguments to run the command with. If ``None`` the arguments
            are gathered from the argument parser. This is automatically set when calling
            sub commands and in most cases should not be set for the root command.

        :return: The status code of the action (0 on success)
        """
        args = args or self.parse_args()

        sub_command_name = getattr(args, self.sub_parser_dest_name, None)
        if sub_command_name:
            sub_commands = self.get_sub_commands()
            cmd_cls = sub_commands[sub_command_name]
            return cmd_cls(sub_command_name).run(args)

        return self.action(args) or 0
