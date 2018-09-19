"""Turning romanized hangul back into jamo and/or hangul."""

import itertools
import logging
import typing as t
import os

from jamo import jamo_to_hangul as jamo_to_single_hangul

if os.environ.get('LOGGING_LEVEL', False):
    logging.basicConfig(level=getattr(logging, os.environ['LOGGING_LEVEL'].upper()))

_LOG = logging.getLogger(__name__)

VOWEL_BASES = ('a', 'i', 'u', 'e', 'o', 'eo', 'eu', 'ae', 'oe', 'ui')

VOWEL_PREFIXES = ('', 'y', 'w')

DOUBLED_CONSONANTS = ('g', 'd', 's', 'j', 'b')

REMAINING_CONSONANTS = ('k', 't', 'ch', 'h', 'p', 'm', 'ng', 'r', 'n')

RELATED_CONSONANTS = ()

ELEMENTS = {
    'a': 'ㅏ', 'ya': 'ㅑ', 'wa': 'ㅘ',
    'i': 'ㅣ', 'wi': 'ㅟ',
    'u': 'ㅜ', 'yu': 'ㅠ',
    'e': 'ㅔ', 'ye': 'ㅖ', 'we': 'ㅞ',
    'o': 'ㅗ', 'yo': 'ㅛ', 'wo': 'ㅝ',
    'eo': 'ㅓ', 'yeo': 'ㅕ',
    'eu': 'ㅡ',
    'ae': 'ㅐ', 'yae': 'ㅒ', 'wae': 'ㅙ',
    'oe': 'ㅚ',
    'ui': 'ㅢ',
    'k': 'ㅋ',
    'g': 'ㄱ', 'gg': 'ㄲ',
    't': 'ㅌ',
    'd': 'ㄷ', 'dd': 'ㄸ',
    's': 'ㅅ', 'ss': 'ㅆ',
    'j': 'ㅈ', 'jj': 'ㅉ',
    'ch': 'ㅊ',
    'h': 'ㅎ',
    'b': 'ㅂ', 'bb': 'ㅃ',
    'p': 'ㅍ',
    'm': 'ㅁ',
    'ng': 'ㅇ',
    'r': 'ㄹ',
    'n': 'ㄴ'}

# synonyms
ELEMENTS['kk'] = ELEMENTS['gg']
ELEMENTS['tt'] = ELEMENTS['dd']
ELEMENTS['pp'] = ELEMENTS['bb']
ELEMENTS['l'] = ELEMENTS['r']

VOWELS = {ELEMENTS[prefix + base]
          for prefix, base in itertools.product(VOWEL_PREFIXES, VOWEL_BASES)
          if prefix + base in ELEMENTS}

DOUBLE_TO_COMBINED = {
    'ㅗㅏ': 'ㅘ', 'ㅜㅣ': 'ㅟ', 'ㅜㅔ': 'ㅞ', 'ㅜㅓ': 'ㅝ', 'ㅗㅐ': 'ㅙ', 'ㅗㅣ': 'ㅚ', 'ㅡㅣ': 'ㅢ',
    'ㄱㄱ': 'ㄲ', 'ㄷㄷ': 'ㄸ', 'ㅅㅅ': 'ㅆ', 'ㅈㅈ': 'ㅉ', 'ㅂㅂ': 'ㅃ', 'ㄱㅅ': 'ᆪ', 'ㄴㅈ': 'ᆬ',
    'ㄴㅎ': 'ᆭ', 'ㄹㄱ': 'ᆰ', 'ㄹㅁ': 'ᆱ', 'ㄹㅂ': 'ᆲ', 'ㄹㅅ': 'ᆳ', 'ㄹㅌ': 'ᆴ', 'ㄹㅍ': 'ᆵ',
    'ㄹㅎ': 'ᆶ', 'ㅂㅅ': 'ᆹ'}

COMBINED_TO_DOUBLE = {v: k for k, v in DOUBLE_TO_COMBINED.items()}

# head jamo

SINGLE_HEAD_JAMO = {'ㄱ', 'ㄴ', 'ㄷ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅅ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'}

DOUBLE_HEAD_JAMO = {'ㄱㄱ', 'ㄷㄷ', 'ㅂㅂ', 'ㅅㅅ', 'ㅈㅈ'}

COMBINED_HEAD_JAMO = {DOUBLE_TO_COMBINED[_] for _ in DOUBLE_HEAD_JAMO}

HEAD_JAMO = SINGLE_HEAD_JAMO | COMBINED_HEAD_JAMO

# body jamo

SINGLE_BODY_JAMO = {'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅛ', 'ㅜ', 'ㅠ', 'ㅡ', 'ㅣ'}

DOUBLE_BODY_JAMO = {'ㅗㅏ', 'ㅗㅐ', 'ㅗㅣ', 'ㅜㅓ', 'ㅜㅔ', 'ㅜㅣ', 'ㅡㅣ'}

COMBINED_BODY_JAMO = {DOUBLE_TO_COMBINED[_] for _ in DOUBLE_BODY_JAMO}

BODY_JAMO = SINGLE_BODY_JAMO | COMBINED_BODY_JAMO

# tail jamo

SINGLE_TAIL_JAMO = {'ㄱ', 'ㄴ', 'ㄷ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅅ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'}

DOUBLE_TAIL_JAMO = {
    'ㄱㄱ', 'ㄱㅅ', 'ㄴㅈ', 'ㄴㅎ', 'ㄹㄱ', 'ㄹㅁ', 'ㄹㅂ', 'ㄹㅅ', 'ㄹㅌ', 'ㄹㅍ', 'ㄹㅎ', 'ㅂㅅ', 'ㅅㅅ'}

COMBINED_TAIL_JAMO = {DOUBLE_TO_COMBINED[_] for _ in DOUBLE_TAIL_JAMO}

TAIL_JAMO = SINGLE_TAIL_JAMO | COMBINED_TAIL_JAMO


ALL_JAMO = HEAD_JAMO | BODY_JAMO | TAIL_JAMO

WHITESPACE = {' ', '\t', '\n', '\r\n'}

PUNCTUATION = {',', '.', '?', '!', ';', ':', '(', ')', '[', ']', '{', '}', '<', '>'}

IGNORED_CHARACTERS = WHITESPACE | PUNCTUATION

DISAMBIGUATORS = {'-'}

ALL_UNAMBIGUOUS_JAMO = ALL_JAMO | DISAMBIGUATORS

INTERRUPTORS = DISAMBIGUATORS | IGNORED_CHARACTERS

SUBSTITUTED = {'ᅪ': 'ㅘ', 'ᅳ': 'ㅡ', 'ᄄ': 'ㄸ', 'ᄍ': 'ㅉ'}


def to_jamo_groups(text: str) -> t.List[t.Tuple[str, int, int]]:
    """Find all groups of jamo (i.e. hangul letters) in a romanized hangul text."""
    jamo_groups = []
    jamo = ''
    begin = 0
    end = 0
    _LOG.debug('to_jamo_groups: %s "%s" %i:%i "%s"', jamo_groups, jamo, begin, end, text)
    while text or jamo:
        if text and text[0] in INTERRUPTORS or not text and jamo:
            if text:
                if jamo:
                    fixup = (0 if text[0] in IGNORED_CHARACTERS else 1)
                    jamo_groups.append((jamo, begin, end + fixup))
                    jamo = ''
                end += 1
                begin = end
                text = text[1:]
            else:
                jamo_groups.append((jamo, begin, end))
                jamo = ''
            _LOG.debug('to_jamo_groups: %s "%s" %i:%i "%s"', jamo_groups, jamo, begin, end, text)
            continue
        added = False
        for length in (3, 2, 1):
            if len(text) < length:
                continue
            if text[:length] in ELEMENTS:
                # assert jamo or begin == end, (jamo, begin, end)
                jamo += ELEMENTS[text[:length]]
                text = text[length:]
                end += length
                _LOG.debug('to_jamo_groups: %s "%s" %i:%i "%s"',
                           jamo_groups, jamo, begin, end, text)
                added = True
                break
        if not added:
            raise ValueError((jamo_groups, jamo, text))
    return jamo_groups


def substitute_text(text: str, replacement: str, begin: int, end: int) -> str:
    return text[:begin] + replacement + text[end:]


def to_jamo(text: str) -> str:
    """Convert romanized korean text into jamo."""
    jamo = text
    jamo_groups = to_jamo_groups(text)
    for jamo_group, begin, end in reversed(jamo_groups):
        _LOG.debug('to_jamo: "%s" %s %i:%i', jamo, jamo_group, begin, end)
        jamo = substitute_text(jamo, jamo_group, begin, end)
    _LOG.debug('to_jamo: "%s"', jamo)
    return jamo


def validate_jamo(jamo: str) -> str:
    """Substitute auto-combining jamo with their not auto combining versions.

    Some jamo has different unicode codes and they cause it to automatically combine into hangul
    and this causes trouble when operating on them.

    For example, ᄄ ᅳ ᆪ automatically combine into 뜫 if there are no spaces between them.
    On the other hand ㄸㅡᆪ give no such trouble and don't merge into 뜫 (here as single character).

    The characters involved:
    https://en.wikipedia.org/wiki/Hangul_Jamo_(Unicode_block)
    https://en.wikipedia.org/wiki/Hangul_Compatibility_Jamo

    To make things worse, sometimes it's versions from one group that merge,
    sometimes from the other.
    """
    if all(_ in ALL_UNAMBIGUOUS_JAMO for _ in jamo):
        return jamo
    _LOG.info('repairing problematic characters in jamo text "%s"', jamo)
    transformed = ''.join(SUBSTITUTED.get(_, _) for _ in jamo)
    assert all(_ in ALL_UNAMBIGUOUS_JAMO for _ in transformed), transformed
    return transformed


def jamo_to_hangul(jamo: str, *,
                   warn: bool = False, limit: int = None, aggressive: bool = True) -> str:
    """Convert a string of jamo into a one or more hangul characters.

    Function can warn if conversion is ambiguous.
    """
    hangul = ''
    jamo = validate_jamo(jamo)
    _LOG.debug('jamo_to_hangul: "%s" "%s"', hangul, jamo)
    while jamo:
        if jamo and jamo[0] in DISAMBIGUATORS:
            jamo = jamo[1:]
            _LOG.debug('jamo_to_hangul: "%s" "%s"', hangul, jamo)
            continue
        jamo = repair_head_jamo(jamo, hangul=hangul, aggressive=aggressive)
        assert jamo[0] in HEAD_JAMO, (hangul, jamo[0], jamo)
        assert len(jamo) >= 2, (hangul, jamo)
        jamo = repair_body_jamo(jamo, hangul=hangul, aggressive=aggressive)
        assert jamo[1] in BODY_JAMO, (hangul, jamo[1], jamo)
        jamo = repair_tail_jamo(jamo, hangul=hangul, aggressive=aggressive)
        if len(jamo) >= 3 and jamo[2] in TAIL_JAMO:
            hangul += jamo_to_single_hangul(jamo[0], jamo[1], jamo[2])
            if warn and len(jamo) >= 4:
                try:
                    short_next = jamo_to_hangul(jamo[2:], warn=False)
                    short = jamo_to_hangul(jamo[:2], warn=False)
                    hangul_next = jamo_to_hangul(jamo[3:], warn=False)
                    _LOG.warning('conversion to hangul is ambiguous for jamo sequence "%s":'
                                 ' both "%s"/"%s" into "%s" and "%s"/"%s" into "%s" are possible',
                                 jamo, jamo[:2], jamo[2:], short + short_next,
                                 jamo[:3], jamo[3:], hangul[-1] + hangul_next)
                except AssertionError:
                    pass
            jamo = jamo[3:]
        else:
            hangul += jamo_to_single_hangul(jamo[0], jamo[1])
            jamo = jamo[2:]
        _LOG.debug('jamo_to_hangul: "%s" "%s"', hangul, jamo)
        if limit is not None and len(hangul) >= limit:
            break
    return hangul


def repair_head_jamo(jamo: str, *, hangul: str = '', aggressive: bool = True) -> str:
    """Insert/substitute jamo at the head position of the jamo sequence to make it canonical."""
    if aggressive and jamo[0:2] in DOUBLE_HEAD_JAMO:
        jamo = DOUBLE_TO_COMBINED[jamo[0:2]] + jamo[2:]
        _LOG.debug('"%s" "%s"', hangul, jamo)
    if jamo[0] in VOWELS:
        jamo = ELEMENTS['ng'] + jamo
        _LOG.debug('"%s" "%s"', hangul, jamo)
    return jamo


def repair_body_jamo(jamo: str, *, hangul: str = '', aggressive: bool = True) -> str:
    """Substitute jamo at the body position of the jamo sequence to make it canonical."""
    if aggressive and len(jamo) >= 3 and jamo[1:3] in DOUBLE_BODY_JAMO:
        jamo = jamo[0] + DOUBLE_TO_COMBINED[jamo[1:3]] + jamo[3:]
        _LOG.debug('"%s" "%s"', hangul, jamo)
    return jamo


def repair_tail_jamo(jamo: str, *, hangul: str = '', aggressive: bool = True) -> str:
    """Substitute jamo at the tail position of the jamo sequence to make it canonical."""
    if aggressive and len(jamo) >= 4 and jamo[2:4] in DOUBLE_TAIL_JAMO:
        jamo = jamo[0:2] + DOUBLE_TO_COMBINED[jamo[2:4]] + jamo[4:]
        _LOG.debug('"%s" "%s"', hangul, jamo)
    return jamo


def to_hangul_groups(jamo_groups: t.Sequence[t.Tuple[str, int, int]],
                     **kwargs) -> t.List[t.Tuple[str, int, int]]:
    """Convert all given jamo sequences into hangul sequences."""
    hangul_groups = []
    for jamo_group, begin, end in jamo_groups:
        hangul = jamo_to_hangul(jamo_group, **kwargs)
        _LOG.debug('to_hangul_groups: "%s" %s %i:%i', hangul, jamo_group, begin, end)
        hangul_groups.append((hangul, begin, end))
    return hangul_groups


def to_hangul(text: str, **kwargs) -> str:
    """Convert romanized korean text into hangul."""
    hangul = text
    hangul_groups = to_hangul_groups(to_jamo_groups(text), **kwargs)
    for hangul_group, begin, end in reversed(hangul_groups):
        _LOG.debug('to_hangul: "%s" %s %i:%i', hangul, hangul_group, begin, end)
        hangul = substitute_text(hangul, hangul_group, begin, end)
    _LOG.debug('to_hangul: "%s"', hangul)
    return hangul
