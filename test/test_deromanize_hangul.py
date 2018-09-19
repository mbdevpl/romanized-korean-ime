"""Tests for hangul deromanization."""

import contextlib
import io
import itertools
import logging
# import os
import unittest

import hangul_romanize
import hangul_romanize.rule
import jamo
import kroman
# import networkx
# import pandas as pd

from deromanize_hangul import \
    IGNORED_CHARACTERS, \
    to_jamo_groups, jamo_to_hangul, to_hangul

_LOG = logging.getLogger(__name__)

# UNAMBIGUOUS_ROMANIZEDD = []

# AMBIGUOUS_ROMANIZED = []

# ROMANIZED = UNAMBIGUOUS_ROMANIZED + AMBIGUOUS_ROMANIZED

UNAMBIGUOUS_STANDARD_EXAMPLES = {
    'san-sung': ('ㅅㅏㄴ-ㅅㅜㅇ', '산숭'),
    'sal-ang': ('ㅅㅏㄹ-ㅏㅇ', '살앙'),
    'sa-rang': ('ㅅㅏ-ㄹㅏㅇ', '사랑'),
    'sa-rang-ha-da': ('ㅅㅏ-ㄹㅏㅇ-ㅎㅏ-ㄷㅏ', '사랑하다'),
    'gal': ('ㄱㅏㄹ', '갈'),
    'sal': ('ㅅㅏㄹ', '살'),
    'hwa': ('ㅎㅘ', '화'),
    'gat-i': ('ㄱㅏㅌ-ㅣ', '같이'),
    'ye-bbeu-da': ('ㅖ-ㅃㅡ-ㄷㅏ', '예쁘다'),
    'ji-geum': ('ㅈㅣ-ㄱㅡㅁ', '지금'),
    'mu-seun yeong-hwa-reul bul-gga-yo?': ('ㅁㅜ-ㅅㅡㄴ-ㅕㅇ-ㅎㅘ-ㄹㅡㄹ-ㅂㅜㄹ-ㄲㅏ-ㅛ', '무슨영화를불까요'),
    'bo-da': ('ㅂㅗ-ㄷㅏ', '보다'),
    'han-gug-eo': ('ㅎㅏㄴ-ㄱㅜㄱ-ㅓ', '한국어'),
    'ho-a': ('ㅎㅗ-ㅏ', '호아'),
    'sa   rang   bang': ('ㅅㅏ-ㄹㅏㅇ-ㅂㅏㅇ', '사랑방'),
    'cha': ('ㅊㅏ', '차'),
    'ne, joh-a-yo.': ('ㄴㅔ-ㅈㅗㅎ-ㅏ-ㅛ', '네좋아요'),
    'ddurm': ('ㄸㅜㄹㅁ', '뚦')}

UNAMBIGUOUS_NONSTANDARD_EXAMPLES = {
    'ddeugs': ('ㄷㄷㅡㄱㅅ', '뜫'),
    'hoa': ('ㅎㅗㅏ', '화')}

NONSTANDARD_EQUIVALENTS = {
    'hwa': 'hoa'}

AMBIGUOUS_EXAMPLES = {
    'sansung', 'gati', 'sarang',
    'ye-bbeuda', 'saranghada', 'jigeum',
    'museun yeonghwareul bulgga-yo?',
    'boda', 'hangugeo', 'hoa'}

BAD_JAMO = [
    ('ㄱㅏㄹㄹㄹ', '갈'),
    ('ㅅㅏㄹㄹㄹ', '살')]

CONFUSING_PAIRS = [
    ('ㅎㅘ', 'ㅎᅪ')]  # jamo ㅘ and ᅪ have different unicode codes


def ignored_in_str(text):
    return ''.join([_ for _ in text if _ in IGNORED_CHARACTERS])


class Tests(unittest.TestCase):

    def test_to_jamo_groups(self):
        for text_, (jamo_, hangul_) in UNAMBIGUOUS_STANDARD_EXAMPLES.items():
            # itertools.chain(
            #    , UNAMBIGUOUS_NONSTANDARD_EXAMPLES.items()):
            with self.subTest(text=text_, jamo=jamo_, hangul=hangul_):
                jamo_groups = to_jamo_groups(text_)
                for i, (jamo_group, begin, end) in enumerate(jamo_groups):
                    with self.subTest(group=jamo_group, bounds=(begin, end)):
                        self.assertIsInstance(jamo_group, str)
                        self.assertIsInstance(begin, int)
                        self.assertIsInstance(end, int)
                        self.assertGreaterEqual(begin, 0)
                        self.assertGreater(end, begin)
                        self.assertLessEqual(end, len(text_))
                        if i > 0:
                            _, _, prev_end = jamo_groups[i - 1]
                            self.assertGreaterEqual(begin, prev_end)
                        if i < len(jamo_groups) - 1:
                            _, next_begin, _ = jamo_groups[i + 1]
                            self.assertLessEqual(end, next_begin)
                # jamo_ = jamo_.split('-')
                self.assertListEqual([jamo_group for jamo_group, _, _ in jamo_groups],
                                     jamo_.split('-'))
                # _LOG.info('%s %i:%i', jamo_to_hangul(jamo_group), begin, end)

    def test_jamo_to_hangul(self):
        for _, (jamo_, hangul_) in UNAMBIGUOUS_STANDARD_EXAMPLES.items():
            hangul = jamo_to_hangul(jamo_)
            self.assertEqual(hangul, hangul_)

    def test_bad_jamo_to_hangul(self):
        for jamo_, _ in BAD_JAMO:
            with self.assertRaises(AssertionError):
                jamo_to_hangul(jamo_)

    def test_compare_kroman(self):
        for example in UNAMBIGUOUS_STANDARD_EXAMPLES:
            hangul = to_hangul(example)
            romanized = kroman.parse(hangul)
            self.assertEqual(example, romanized)

    def test_compare_hangul_romanize(self):
        romanizer = hangul_romanize.core.Transliter(hangul_romanize.rule.academic)
        for example in UNAMBIGUOUS_STANDARD_EXAMPLES:
            hangul = to_hangul(example)
            romanized = romanizer.translit(hangul)
            example = example.replace('-', '').replace('r', 'l') \
                .replace('gg', 'kk').replace('bb', 'pp').replace('dd', 'tt')
            romanized = romanized.replace('-', '')
            self.assertEqual(example, romanized)

    def test_compare_jamo(self):
        for good, bad in NONSTANDARD_EQUIVALENTS.items():
            good, _ = UNAMBIGUOUS_STANDARD_EXAMPLES[good]
            bad, _ = UNAMBIGUOUS_NONSTANDARD_EXAMPLES[bad]
            with self.subTest(good=good, bad=bad):
                sio = io.StringIO()
                self.assertEqual(''.join(jamo.jamo_to_hangul(*good)), jamo_to_hangul(good))
                # jamo.stderr = sio
                with contextlib.redirect_stderr(sio):
                    with self.assertRaises(jamo.InvalidJamoError):
                        jamo.jamo_to_hangul(*bad)
                self.assertEqual(''.join(jamo.jamo_to_hangul(*good)), jamo_to_hangul(bad))

    def test_other_compare_jamo(self):
        for hangul in '뜫':
            jamo_ = ''.join(jamo.hangul_to_jamo(hangul))
            _LOG.debug('%s %s %s', jamo_, len(jamo_), jamo_[2])
            jamo_list = list(jamo.hangul_to_jamo(hangul))
            _LOG.debug('%s %s %s', jamo_list, len(jamo_list), jamo_list[2])
            romanized = kroman.parse(hangul)
            hangul_from_jamo = jamo_to_hangul(jamo_)
            hangul_deromanized = to_hangul(romanized)
            self.assertEqual(hangul, hangul_from_jamo)
            self.assertEqual(hangul, hangul_deromanized)

    def test_confusing_char(self):
        for good, bad in CONFUSING_PAIRS:
            with self.subTest(good=good, bad=bad):
                self.assertNotEqual(good, bad)
                self.assertEqual(list(jamo.jamo_to_hangul(*good))[0], jamo_to_hangul(good))
                self.assertEqual(list(jamo.jamo_to_hangul(*bad))[0], jamo_to_hangul(bad))

    def test_preserve_ignored_characters(self):
        for example in itertools.chain(
                UNAMBIGUOUS_STANDARD_EXAMPLES.keys(), UNAMBIGUOUS_NONSTANDARD_EXAMPLES.keys(),
                AMBIGUOUS_EXAMPLES):
            with self.subTest(example=example):
                ignored_str = ignored_in_str(example)
                hangul = to_hangul(example)
                ignored_hangul_str = ignored_in_str(hangul)
                self.assertEqual(ignored_str, ignored_hangul_str)

    def test_nonstandard(self):
        for _, (jamo_, hangul) in UNAMBIGUOUS_NONSTANDARD_EXAMPLES.items():
            with self.subTest(jamo=jamo_, hangul=hangul):
                hangul_ = jamo_to_hangul(jamo_)
                self.assertEqual(hangul_, hangul)

    def test_errors(self):
        with self.assertRaises(ValueError):
            to_jamo_groups('fujisan')
        with self.assertRaises(AssertionError):
            jamo_to_hangul('hello')
        with self.assertRaises(AssertionError):
            jamo_to_hangul('ㅍhello')
        with self.assertRaises(ValueError):
            to_hangul('---ㅍㅛ')
