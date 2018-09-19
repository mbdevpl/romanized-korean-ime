.. role:: bash(code)
    :language: bash

.. role:: python(code)
    :language: python


====================
Romanized Korean IME
====================

.. image:: https://img.shields.io/github/license/mbdevpl/romanized-korean-ime.svg
    :target: https://github.com/mbdevpl/romanized-korean-ime/blob/master/NOTICE
    :alt: license


Romanized Korean Input Method Editor (IME) is a piece of software that
lets you type latin script letters (e.g. a, b, s, ...),
converts them to jamo on-the-fly to jamo (e.g. ㅏ, ㅂ, ㅅ, ...)
and converts jamo on-the-fly to hangul (e.g. 앖, ...).

Currently this package is just a proof-of-concept for how romanized Korean IME could work.

.. contents::
    :backlinks: none


Introduction
============

Currently, the package boils down to a command-line utility that simply prints output to stdout.


Running from command-line
-------------------------

Simply run below command to run the module.

.. code:: bash

    python3 -m romanized_korean_ime


This will read alphabetic characters one by one and convert them to Hangul as you type them.

Special characters are:

*   minus ``-`` character is used to disambiguate,
    e.g. ``sarang`` converts into ``살앙`` but ``sa-rang`` into ``사랑``
*   space, tab, comma, question mark, semicolon act as separators
*   backspace deletes last entered character
*   newline exits the command-line tool

Using as Python module
----------------------

Not really supported at this point.

.. code:: python

    import romanized_korean_ime


Requirements
============

Python version 3.6 or later.

Python libraries as specified in `<requirements.txt>`_.

Building and running tests additionally requires packages listed in `<test_requirements.txt>`_.
