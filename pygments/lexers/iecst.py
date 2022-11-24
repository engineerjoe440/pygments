"""
    pygments.lexers.iecst
    ~~~~~~~~~~~~~~~~~~~~~

    Lexer for IEC 61131-3 Structured Text.
    Reference: https://en.wikipedia.org/wiki/Structured_text

    :copyright: Copyright 2006-2022 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re

from pygments.lexer import RegexLexer, include, bygroups, using, this, \
    default, words
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Whitespace

__all__ = ['IecstLexer']


class IecstLexer(RegexLexer):
    """
    For `IEC 61131-3 Structured Text
    <https://en.wikipedia.org/wiki/Structured_text>`_ source code.

    .. versionadded:: TODO
    """
    name = 'IEC Structured Text'
    aliases = ['iecst', 'st']
    filenames = ['*.st']
    mimetypes = ['text/x-iecst']

    # Hexadecimal part in an hexadecimal integer/floating-point literal.
    # This includes decimal separators matching.
    _hexpart = r'[0-9a-fA-F](\'?[0-9a-fA-F])*'
    # Decimal part in an decimal integer/floating-point literal.
    # This includes decimal separators matching.
    _decpart = r'\d(\'?\d)*'
    # Integer literal suffix (e.g. 'ull' or 'll').
    _intsuffix = r'(([uU][lL]{0,2})|[lL]{1,2}[uU]?)?'

    # Identifier regex with C and C++ Universal Character Name (UCN) support.
    _ident = r'(?!\d)(?:[\w$]|\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8})+'
    _namespaced_ident = r'(?!\d)(?:[\w$]|\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8}|::)+'

    # Single and multiline comment regexes
    # Beware not to use *? for the inner content! When these regexes
    # are embedded in larger regexes, that can cause the stuff*? to
    # match more than it would have if the regex had been used in
    # a standalone way ...
    _comment_single = r'//(?:.|(?<=\\)\n)*\n'
    _comment_multiline = r'\((?:\\\n)?[*](?:[^*]|[*](?!(?:\\\n)?/))*[*](?:\\\n)?\)'

    # Regex to match optional comments
    _possible_comments = rf'\s*(?:(?:(?:{_comment_single})|(?:{_comment_multiline}))\s*)*'

    tokens = {
        'whitespace': [
            # Labels:
            (r'\n', Whitespace),
            (r'[^\S\n]+', Whitespace),
            (r'\\\n', Text),  # line continuation
            (_comment_single, Comment.Single),
            (_comment_multiline, Comment.Multiline),
            # Open until EOF, so no ending delimiter
            (r'/(\\\n)?[*][\w\W]*', Comment.Multiline),
        ],
        'keywords': [
            (words(('IF', 'THEN', 'ELSIF', 'ELSE', 'END_IF', 'FOR', 'DO',
                    'END_FOR', 'WHILE', 'END_WHILE', 'REPEAT', 'UNTIL', 'BREAK',
                    'CONTINUE', 'RETURN', 'END_REPEAT', 'CONSTANT', 'VAR',
                    'VAR_INPUT', 'VAR_OUTPUT', 'VAR_STAT', 'VAR_IN_OUT', 'OF',
                    'VAR_GLOBAL', 'END_VAR', 'PUBLIC', 'PRIVATE', 'INTERNAL',
                    'PROTECTED', 'FUNCTION', 'PROGRAM', 'FUNCTION_BLOCK',
                    'CASE', 'END_CASE', 'END_FUNCTION', 'END_PROGRAM',
                    'END_FUNCTION_BLOCK', 'MOD', 'ABS', 'ACOS', 'ASIN', 'ATAN',
                    'COS', 'EXP', 'EXPT', 'LN', 'LOG', 'SIN', 'SQRT', 'TAN',
                    'SEL', 'MAX', 'MIN', 'LIMIT', 'MUX', 'SHL', 'SHR', 'ROL',
                    'ROR', 'INDEXOF', 'SIZEOF', 'ADR', 'REF', 'ADRINST',
                    'BITADR', 'ADD', 'MUL', 'DIV', 'SUB', 'TRUNC', 'MOVE',
                    ), suffix=r'\b'),
             Keyword),
        ],
        'types': [
            (words(('BOOL', 'BYTE', 'WORD', 'DWORD', 'LWORD', 'SINT', 'USINT',
                    'INT', 'UINT', 'DINT', 'UDINT', 'UDINT', 'LINT', 'ULINT',
                    'REAL', 'LREAL', 'STRING', 'WSTRING', 'TIME', 'LTIME',
                    'TIME_OF_DAY', 'TOD', 'DATE', 'DATE_AND_TIME', 'DT', 
                    'POINTER', 'ARRAY', 'REFERENCE'),
                    suffix=r'\b'),
             Keyword.Type),
        ],
        'statements': [
            include('keywords'),
            include('types'),
            (r'([LuU]|u8)?(")', bygroups(String.Affix, String), 'string'),
            (r"([LuU]|u8)?(')(\\.|\\[0-7]{1,3}|\\x[a-fA-F0-9]{1,2}|[^\\\'\n])(')",
             bygroups(String.Affix, String.Char, String.Char, String.Char)),

             # Hexadecimal floating-point literals (C11, C++17)
            (r'0[xX](' + _hexpart + r'\.' + _hexpart + r'|\.' + _hexpart +
             r'|' + _hexpart + r')[pP][+-]?' + _hexpart + r'[lL]?', Number.Float),

            (r'(-)?(' + _decpart + r'\.' + _decpart + r'|\.' + _decpart + r'|' +
             _decpart + r')[eE][+-]?' + _decpart + r'[fFlL]?', Number.Float),
            (r'(-)?((' + _decpart + r'\.(' + _decpart + r')?|\.' +
             _decpart + r')[fFlL]?)|(' + _decpart + r'[fFlL])', Number.Float),
            (r'(-)?0[xX]' + _hexpart + _intsuffix, Number.Hex),
            (r'(-)?0[bB][01](\'?[01])*' + _intsuffix, Number.Bin),
            (r'(-)?0(\'?[0-7])+' + _intsuffix, Number.Oct),
            (r'(-)?' + _decpart + _intsuffix, Number.Integer),
            (r':=|:|\+|-|\*|/|>|<', Operator),
            (r'''(?x)\b(?:
                AND|OR|NOT|
                TO_(BOOL|BYTE|D?L?WORD|L?TIME|DATE|DT|TOD|W?CHAR|W?STRING|U?S?D?L?INT|L?REAL)|
                (ANY|BOOL|BYTE|D?L?WORD|L?TIME|DATE|DT|TOD|W?CHAR|W?STRING|U?S?D?L?INT|L?REAL)_TO_(BOOL|BYTE|D?L?WORD|L?TIME|DATE|DT|TOD|W?CHAR|W?STRING|U?S?D?L?INT|L?REAL)
              )\b''',
             Operator.Word),
            (r'[()\[\],.]', Punctuation),
            (r'(true|false|null)\b', Name.Builtin),
            (_ident, Name)
        ],
        'string': [
            (r'"', String, '#pop'),
            (r'\\([\\abfnrtv"\']|x[a-fA-F0-9]{2,4}|'
             r'u[a-fA-F0-9]{4}|U[a-fA-F0-9]{8}|[0-7]{1,3})', String.Escape),
            (r'[^\\"\n]+', String),  # all other characters
            (r'\\\n', String),  # line continuation
            (r'\\', String),  # stray backslash
        ],
        'root': [
            include('whitespace'),
            include('keywords'),
            include('types'),
            default('statement'),
        ],
        'statement': [
            include('whitespace'),
            include('statements'),
            (r'\}', Punctuation),
            (r'[{;]', Punctuation, '#pop'),
        ],
    }