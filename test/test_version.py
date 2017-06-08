"""Tests of version string parsing and generation."""

import unittest

from version_query.version import Version


class Tests(unittest.TestCase):

    def test_version_parse(self):
        Version.parse_str('0')
        Version.parse_str('42')
        Version.parse_str('0.1')
        Version.parse_str('8.0')
        Version.parse_str('16.04')
        Version.parse_str('0.54.0')
        Version.parse_str('1.0.0')
        Version.parse_str('1.0.0.4')
        Version.parse_str('1.0.0.8')
        Version.parse_str('1.0.0.rc3')
        Version.parse_str('1.0.1.dev0')
        Version.parse_str('0.14.4.dev5+84e1d430')

    def test_version_generate(self):
        Version.generate_str(0)
        Version.generate_str(42)
        Version.generate_str(0, 1)
        Version.generate_str(8, 0)
        Version.generate_str(16, 4)
        Version.generate_str(0, 54, 0)
        Version.generate_str(1, 0, 0)
        Version.generate_str(1, 0, 1, 'dev', 0)
        Version.generate_str(0, 14, 4, 'dev', 5, '84e1d430')
