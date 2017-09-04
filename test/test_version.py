"""Tests of version string parsing and generation."""

import unittest

import packaging.version

from version_query.version import Version

CASES = {
    '0': ((0,), {}),
    '42': ((42,), {}),
    '5+d2a610ba': ((5,), {'commit_sha': 'd2a610ba'}),
    '0.1': ((0, 1), {}),
    '8.0': ((8, 0), {}),
    '16.4': ((16, 4), {}),
    '5.0+f753199e': ((5, 0), {'commit_sha': 'f753199e'}),
    '0.54.0': ((0, 54, 0), {}),
    '1.0.0': ((1, 0, 0), {}),
    '7.0.42+1d7b090a': ((7, 0, 42), {'commit_sha': '1d7b090a'}),
    '1.0.0.4': ((1, 0, 0, None, 4), {}),
    '2.0.0.8+cc81cee': ((2, 0, 0, None, 8, 'cc81cee'), {}),
    '4.5.0.dev': ((4, 5, 0, 'dev'), {}),
    '1.0.0.rc3': ((1, 0, 0, 'rc', 3), {}),
    '1.0.1.dev0': ((1, 0, 1, 'dev', 0), {}),
    '0.4.4.dev5+84e1d430': ((0, 4, 4, 'dev', 5, '84e1d430'), {})}

KWARG_NAMES = ('major', 'minor', 'release', 'suffix', 'patch', 'commit_sha')


class Tests(unittest.TestCase):

    def test_version_parse(self):
        for version_str, (args, kwargs) in CASES.items():
            version_tuple = tuple([
                args[i] if i < len(args) else (kwargs[KWARG_NAMES[i]] if KWARG_NAMES[i] in kwargs else None)
                for i in range(0, 6)])
            with self.subTest(version_str=version_str, version_tuple=version_tuple):
                self.assertEqual(Version.parse_str(version_str), version_tuple)

    def test_version_parse_bad(self):
        with self.assertRaises(packaging.version.InvalidVersion):
            Version.parse_str('hello world')

    def test_version_generate(self):
        for result, (args, kwargs) in CASES.items():
            with self.subTest(args=args, kwargs=kwargs, result=result):
                self.assertEqual(Version.generate_str(*args, **kwargs), result)

    def test_version_generate_bad(self):
        with self.assertRaises(NotImplementedError):
            Version.generate_str()
        with self.assertRaises(NotImplementedError):
            Version.generate_str(5, patch=2)
        with self.assertRaises(NotImplementedError):
            Version.generate_str(1, release=13)
