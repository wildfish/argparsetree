import string
from argparse import ArgumentParser

from unittest import TestCase

from hypothesis import given
from hypothesis.strategies import text, dictionaries, lists, integers
from mock import Mock
from random import choice

from argparsetree import BaseCommand


class BaseSubParserDestName(TestCase):
    def test_name_is_none___argument_is_stored_in_sub_command(self):
        command = BaseCommand()

        self.assertEqual('sub_command', command.sub_parser_dest_name)

    @given(text(min_size=1, max_size=10, alphabet=string.printable))
    def test_name_is_not_none___argument_is_stored_in_name_plus_sub_command(self, name):
        command = BaseCommand(name)

        self.assertEqual(name + '__sub_command', command.sub_parser_dest_name)


class BaseParseArgs(TestCase):
    @given(dictionaries(text(min_size=1, max_size=10, alphabet=string.ascii_letters), text(min_size=1, max_size=10, alphabet=string.ascii_letters), min_size=1, max_size=10))
    def test_command_has_args_set___args_are_stored_in_the_result(self, arg_vals):
        class Cmd(BaseCommand):
            def add_args(self, parser):
                for k in arg_vals.keys():
                    parser.add_argument(k)

        args = Cmd(argv=list(arg_vals.values())).parse_args()

        for k, v in arg_vals.items():
            self.assertEqual(v, getattr(args, k))

    @given(
        lists(text(min_size=1, max_size=10, alphabet=string.ascii_letters), min_size=1, max_size=10),
    )
    def test_command_has_sub_command_arg_set___sub_command_is_called(self, sub_parser_names):
        class SubCmd(BaseCommand):
            pass

        class Cmd(BaseCommand):
            sub_commands = dict(
                (n, SubCmd) for n in sub_parser_names
            )

        selected = choice(sub_parser_names)

        command = Cmd(argv=[selected])
        args = command.parse_args()

        self.assertEqual(selected, getattr(args, command.sub_parser_dest_name))


class BaseAction(TestCase):
    def test_action_is_not_implemented_by_command___the_action_help_is_printed(self):
        command = BaseCommand()
        command.arg_parser.print_help = Mock()

        self.assertEqual(1, command.action(None))
        command.arg_parser.print_help.assert_called_once_with()


class BaseRun(TestCase):
    @given(
        integers(min_value=0, max_value=10),
        dictionaries(text(min_size=1, max_size=10, alphabet=string.ascii_letters), text(min_size=1, max_size=10, alphabet=string.ascii_letters), min_size=1, max_size=10),
    )
    def test_command_has_no_sub_parser___action_from_command_is_called(self, action_res, args):
        action_mock = Mock(return_value=action_res)

        class Cmd(BaseCommand):
            def add_args(self, parser):
                for k in args.keys():
                    parser.add_argument(k)

            def action(self, args):
                return action_mock(args)

        command = Cmd(argv=list(args.values()))
        res = command.run()

        self.assertEqual(res, action_res)
        action_mock.assert_called_once_with(command.parse_args())

    @given(
        integers(min_value=0, max_value=10),
        integers(min_value=11, max_value=20),
        lists(text(min_size=1, max_size=10, alphabet=string.ascii_letters), min_size=1, max_size=10),
    )
    def test_command_has_sub_command___action_from_sub_command_is_called(self, action_res, other_action_res, sub_parser_names):
        selected = choice(sub_parser_names)

        action_mock = Mock(return_value=action_res)
        other_action_mock = Mock(return_value=other_action_res)

        class SubCmd(BaseCommand):
            def action(self, args):
                return action_mock(args)

        class OtherSubCmd(BaseCommand):
            def action(self, args):
                return other_action_mock(args)

        class Cmd(BaseCommand):
            sub_commands = dict(
                (n, (SubCmd if n == selected else OtherSubCmd)) for n in sub_parser_names
            )

        command = Cmd(argv=[selected])
        res = command.run()

        self.assertEqual(res, action_res)
        action_mock.assert_called_once_with(command.parse_args())
        other_action_mock.assert_not_called()

    @given(
        integers(min_value=0, max_value=10),
        integers(min_value=11, max_value=20),
        lists(text(min_size=1, max_size=10, alphabet=string.ascii_letters), min_size=1, max_size=10),
        text(min_size=1, max_size=10, alphabet=string.ascii_letters),
    )
    def test_command_has_grandchild_sub_command___action_from_grandchild_sub_command_is_called(self, action_res, other_action_res, sub_parser_names, command_name):
        selected = choice(sub_parser_names)

        action_mock = Mock(return_value=action_res)
        other_action_mock = Mock(return_value=other_action_res)

        class SubCmd(BaseCommand):
            def action(self, args):
                return action_mock(args)

        class OtherSubCmd(BaseCommand):
            def action(self, args):
                return other_action_mock(args)

        class ChildCmd(BaseCommand):
            sub_commands = dict(
                (n, (SubCmd if n == selected else OtherSubCmd)) for n in sub_parser_names
            )

        class Cmd(BaseCommand):
            sub_commands = {
                'child': ChildCmd
            }

        command = Cmd(argv=['child', selected])
        res = command.run()

        self.assertEqual(res, action_res)
        action_mock.assert_called_once_with(command.parse_args())
        other_action_mock.assert_not_called()

    def test_action_returns_none___run_returns_zero(self):
        class Cmd(BaseCommand):
            def action(self, args):
                return None

        command = Cmd(argv=[])
        res = command.run()

        self.assertEqual(res, 0)


class BaseGetDescription(TestCase):
    def test_command_has_description_and_no_doc_string___description_is_description(self):
        class Cmd(BaseCommand):
            description = 'The commands description.'

        cmd = Cmd()

        self.assertEqual('The commands description.', cmd.get_description())

    def test_command_has_description_and_doc_string___description_is_description(self):
        class Cmd(BaseCommand):
            """
            The doc string description. And extra help.
            """
            description = 'The commands description.'

        cmd = Cmd()

        self.assertEqual('The commands description.', cmd.get_description())

    def test_command_has_doc_string_but_no_description___first_doc_string_sentence_is_description(self):
        class Cmd(BaseCommand):
            """
            The doc string description. And extra help.
            """

        cmd = Cmd()

        self.assertEqual('The doc string description.', cmd.get_description())


class BaseGetRootParser(TestCase):
    def test_no_argument_parser_class_is_set___instance_of_argparse_is_returned(self):
        class Cmd(BaseCommand):
            pass

        cmd = Cmd()

        self.assertIsInstance(cmd.get_root_argparser(), ArgumentParser)

    def test_argument_parser_class_is_set___instance_of_defined_class_is_set(self):
        class CustomParser(ArgumentParser):
            pass

        class Cmd(BaseCommand):
            arg_parse_class = CustomParser

        cmd = Cmd()

        self.assertIsInstance(cmd.get_root_argparser(), CustomParser)


class BaseGetHelp(TestCase):
    def test_command_has_help_and_no_doc_string___description_is_description(self):
        class Cmd(BaseCommand):
            help = 'The commands help text.'

        cmd = Cmd()

        self.assertEqual('The commands help text.', cmd.get_help())

    def test_command_has_description_and_doc_string___description_is_description(self):
        class Cmd(BaseCommand):
            """
            The doc string description. And extra help.
            """
            help = 'The commands help text.'

        cmd = Cmd()

        self.assertEqual('The commands help text.', cmd.get_help())

    def test_command_has_doc_string_but_no_description___first_doc_string_sentence_is_description(self):
        class Cmd(BaseCommand):
            """
            The doc string description. And extra help.
            """

        cmd = Cmd()

        self.assertEqual('The doc string description. And extra help.', cmd.get_help())
