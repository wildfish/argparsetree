#!/usr/bin/env python

import sys
from argparsetree import BaseCommand


class CleanFooCommand(BaseCommand):
    description = 'Cleans up the foo object'

    def add_args(self, parser):
        parser.add_argument('target', help='The foo file to clean up')
        parser.add_argument('-y', '--yes', help='Automatic answer yes to prompts', action='store_true')

    def action(self, args):
        # do cleaning
        return 0


class CheckFooCommand(BaseCommand):
    description = 'Checks the integrity of a foo object'

    def add_args(self, parser):
        parser.add_argument('target', help='The foo file to clean up')
        parser.add_argument('-y', '--yes', help='Automatic answer yes to prompts', action='store_true')

    def action(self, args):
        # do cleaning
        return 0


class FooCommand(BaseCommand):
    description = 'Do things with foos'
    sub_commands = {
        'check': CheckFooCommand,
        'clean': CleanFooCommand,
        # more sub commands here
    }


class RootCommand(BaseCommand):
    description = 'My fancy CLI'
    sub_commands = {
        'foo': FooCommand,
        # more sub commands here
    }


if __name__ == '__main__':
    sys.exit(RootCommand().run())
