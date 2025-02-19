"""Patterns for recognising parts of version strings and parsing them."""

import re

# pylint: disable = consider-using-f-string

_NUMBER = r'(?:0|[123456789][0123456789]*)'
# _SHA = r'[0123456789abcdef]+'
_LETTERS = r'(?:[abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ]+)'
LETTERS = re.compile(_LETTERS)
_ALPHANUMERIC = r'(?:[0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ]+)'
ALPHANUMERIC = re.compile(_ALPHANUMERIC)
_SEP = r'(?:[\.-])'

_RELEASE_PARTS = \
    r'(?P<major>{n})(?:\.(?P<minor>{n}))?(?:\.(?P<patch>{n}))?'.format(n=_NUMBER)
RELEASE = re.compile(_RELEASE_PARTS)

_PRE_SEPARATOR = rf'(?P<preseparator>{_SEP})'
_PRE_TYPE = rf'(?P<pretype>{_LETTERS})'
_PRE_PATCH = rf'(?P<prepatch>{_NUMBER})'
_PRE_RELEASE_PART = rf'{_PRE_SEPARATOR}?{_PRE_TYPE}?{_PRE_PATCH}?'
PRE_RELEASE_PART = re.compile(_PRE_RELEASE_PART)
_PRE_RELEASE_PARTS = r'(?:{0}{2})|(?:{0}?{1}{2}?)'.format(_SEP, _LETTERS, _NUMBER)
PRE_RELEASE = re.compile(_PRE_RELEASE_PARTS)
# PRE_RELEASE_CHECK = re.compile(rf'(?:{_PRE_RELEASE_PARTS})+')

_LOCAL_SEPARATOR = rf'({_SEP})'
_LOCAL_PART = rf'({_ALPHANUMERIC})'
_LOCAL_PARTS = rf'\+{_LOCAL_PART}(?:{_LOCAL_SEPARATOR}{_LOCAL_PART})*'
LOCAL = re.compile(_LOCAL_PARTS)


_RELEASE = r'(?P<release>{n}(?:\.{n})?(?:\.{n})?)'.format(n=_NUMBER)
_PRE_RELEASE = r'(?P<prerelease>(?:(?:{0}{2})|(?:{0}?{1}{2}?))+)'.format(_SEP, _LETTERS, _NUMBER)
_LOCAL = r'(?P<local>\+{0}([\.-]{0})*)'.format(_ALPHANUMERIC)
# _NAMED_PARTS_COUNT = 3 + 3
_VERSION = rf'{_RELEASE}{_PRE_RELEASE}?{_LOCAL}?'
VERSION = re.compile(_VERSION)
