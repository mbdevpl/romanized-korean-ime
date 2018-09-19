
import argparse
import logging
import pprint

import readchar

from .deromanize_hangul import ELEMENTS, DOUBLE_TO_COMBINED
from .korean_ime import GreedyKoreanIME

_INTERRUPTS = {chr(3)}

_BACKSPACE = '\x7f'

_ENDINGS = {'\n', '\r'}


def n_col_print(iterable, cols: int = 3, col_sep: str = '\t'):
    i = 0
    for i, item in enumerate(iterable):
        print(item, end='', flush=True)
        if (i + 1) % cols == 0:
            print()
        else:
            print(col_sep, end='', flush=True)
    if (i + 1) % cols != 0:
        print()


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description='''Romanized Korean Input Method Editor (IME).''',
        epilog='Copyright 2018 Mateusz Bysiek  https://mbdevpl.github.io/')
    parser.add_argument(
        '--help-input', action='store_true',
        help='show all romanized input that will be converted into hangul')
    return parser.parse_args(args)


def main(args=None):
    """Entry point of command-line interface."""
    parsed_args = parse_args(args)
    if parsed_args.help_input:
        print('All romanized input that will be converted into jamo:')
        _ = ['{:3}: {}'.format(romanization, jamo) for romanization, jamo in ELEMENTS.items()]
        n_col_print(_, 6, '    ')
        # pprint.pprint(_)  # print('\n'.join(_))
        print('All pairs of simple jamo that will be combined into a single two-component jamo:')
        _ = ['{}: {}  '.format(pair, combined) for pair, combined in DOUBLE_TO_COMBINED.items()]
        n_col_print(_, 4)
        # pprint.pprint(_)  # print('\n'.join(_))
        return
    logging.basicConfig(level=logging.DEBUG, filename='korean_ime.log')
    # logging.getLogger('deromanize_hangul').setLevel(logging.INFO)
    ime = GreedyKoreanIME()
    char = ''
    while char not in _ENDINGS:
        char = readchar.readchar()
        if char == _BACKSPACE:
            output = ime.type_backspace()
        else:
            output = ime.type_printable_character(char)
        if output:
            print(output, end='', flush=True)
        if char in _INTERRUPTS:
            raise KeyboardInterrupt()
    print()
