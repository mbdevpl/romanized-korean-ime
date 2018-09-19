"""IME input alike the Japanese IME but for hangul."""

import logging
# import typing as t

from .deromanize_hangul import to_jamo_groups, substitute_text, to_hangul_groups, to_jamo

_LOG = logging.getLogger(__name__)


class KoreanIME:

    """Korean IME."""

    def __init__(self):
        # stores text that could not be converted yet
        self._unconverted_text = ''

        # text that could be already converted to jamo but not to hangul
        self._unconverted_jamo = ''
        self._jamo_text = ''

        # text that could be already converted to hangul
        self._hangul = ''
        self._hangul_jamo = ''
        self._hangul_text = ''

    @property
    def text(self):
        return self._hangul_text + self._jamo_text + self._unconverted_text

    @property
    def jamo(self):
        return self._hangul_jamo + self._unconverted_jamo

    @property
    def hangul(self):
        return self._hangul

    @property
    def output(self):
        return self._hangul + self._unconverted_jamo + self._unconverted_text


class GreedyKoreanIME(KoreanIME):

    """Greedy Korean IME.

    With each keystroke this IME will:
    - try to convert as much text as possible into jamo
    - and try to convert as much as possible of jamo into hangul.
    """

    def __init__(self):
        super().__init__()
        # self._jamo_groups = ''

    def convert_text_to_jamo(self):
        text = self.text
        if not text:
            return
        _LOG.debug('converting %s to jamo', repr(text))
        jamo_groups = []
        end_of_conversion = 0
        for i in range(len(text), 0, -1):
            try:
                jamo_groups = to_jamo_groups(text[:i])
                end_of_conversion = i
                _LOG.debug('settled on converting "%s"', text[:end_of_conversion])
                break
            except ValueError:
                continue
        if end_of_conversion == 0:
            return
        unconverted_jamo = text[:end_of_conversion]
        for jamo, begin, end in reversed(jamo_groups):
            unconverted_jamo = substitute_text(unconverted_jamo, jamo, begin, end)
        self._unconverted_text = text[end_of_conversion:]
        self._unconverted_jamo = unconverted_jamo
        self._jamo_text = text[:end_of_conversion]
        self._hangul = ''
        self._hangul_jamo = ''
        self._hangul_text = ''

    def convert_jamo_to_hangul(self):
        text = self._hangul_text + self._jamo_text
        if not text:
            return
        _LOG.debug('converting %s to hangul', repr(text))
        jamo_groups = []
        hangul_groups = []
        end_of_conversion = 0
        for i in range(len(text), 0, -1):
            try:
                _LOG.debug('trying %i', i)
                jamo_groups = to_jamo_groups(text[:i])
                hangul_groups = to_hangul_groups(jamo_groups)
                if not hangul_groups:
                    continue
                _LOG.debug('settled on converting %i jamo groups: %s',
                           len(hangul_groups), hangul_groups)
                end_of_conversion = hangul_groups[-1][2]
                break
            except AssertionError:
                continue
        if end_of_conversion == 0:
            return

        hangul = text[:end_of_conversion]
        for hangul_group, begin, end in reversed(hangul_groups):
            hangul = substitute_text(hangul, hangul_group, begin, end)
        jamo = text[:end_of_conversion]
        for jamo_group, begin, end in reversed(jamo_groups[:len(hangul_groups)]):
            jamo = substitute_text(jamo, jamo_group, begin, end)

        self._unconverted_jamo = to_jamo(text[end_of_conversion:])
        self._jamo_text = text[end_of_conversion:]
        self._hangul = hangul
        self._hangul_jamo = jamo
        self._hangul_text = text[:end_of_conversion]

    def type_printable_character(self, char: str) -> str:
        """Type one printable character into the IME."""
        _LOG.info('typed "%s"', char)
        output = self.output
        output_len = len(output) + len(self._unconverted_jamo) + len(self._hangul)

        self._unconverted_text = self._hangul_text + self._jamo_text + self._unconverted_text
        self._unconverted_jamo = ''
        self._jamo_text = ''
        self._hangul = ''
        self._hangul_jamo = ''
        self._hangul_text = ''

        self._unconverted_text += char
        self.convert_text_to_jamo()
        self.convert_jamo_to_hangul()
        _LOG.info('after conversion: "%s" ("%s", "%s"), "%s" ("%s"), "%s"',
                  self._hangul, self._hangul_jamo, self._hangul_text,
                  self._unconverted_jamo, self._jamo_text, self._unconverted_text)
        _LOG.debug('all hangul: "%s"', self.hangul)
        _LOG.debug('all jamo: "%s"', self.jamo)
        _LOG.debug('all text: "%s"', self.text)

        deleted_output = output_len * '\b'
        _LOG.debug('previous output %s, len=%i', repr(output), output_len)
        _LOG.debug('output deletion mask %s, len=%i', repr(deleted_output), len(deleted_output))
        _LOG.debug('current output %s, len=%i', repr(self.output), len(self.output))

        output_delta = '{}{}{}{}'.format(
            deleted_output, output_len * ' ', deleted_output, self.output)
        return output_delta

    def type_backspace(self) -> str:
        """Type backspace into the IME."""
        _LOG.info('typed backspace')
        output = self.output
        output_len = len(output) + len(self._unconverted_jamo) + len(self._hangul)

        self._unconverted_text = self._hangul_text + self._jamo_text + self._unconverted_text
        self._unconverted_jamo = ''
        self._jamo_text = ''
        self._hangul = ''
        self._hangul_jamo = ''
        self._hangul_text = ''

        self._unconverted_text = self._unconverted_text[:-1]
        self.convert_text_to_jamo()
        self.convert_jamo_to_hangul()
        _LOG.info('after conversion: "%s" ("%s", "%s"), "%s" ("%s"), "%s"',
                  self._hangul, self._hangul_jamo, self._hangul_text,
                  self._unconverted_jamo, self._jamo_text, self._unconverted_text)

        deleted_output = output_len * '\b'

        output_delta = '{}{}{}{}'.format(
            deleted_output, output_len * ' ', deleted_output, self.output)
        return output_delta
