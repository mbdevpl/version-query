"""Tests of version string parsing and generation."""

import unittest

import packaging.version
import pkg_resources
import semver

from version_query.version import Version, VersionNew

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

NEW_CASES = {
    '0': ((0,), {}),
    '42': ((42,), {}),
    '5+d2a610ba': ((5,), {'local': 'd2a610ba'}),
    '0.1': ((0, 1), {}),
    '8.0': ((8, 0), {}),
    '16.4': ((16, 4), {}),
    '5.0+f753199e': ((5, 0), {'local': 'f753199e'}),
    '0.54.0': ((0, 54, 0), {}),
    '1.0.0': ((1, 0, 0), {}),
    '7.0.42+1d7b090a': ((7, 0, 42), {'local': '1d7b090a'}),
    '1.0.0.4': ((1, 0, 0, '.', None, 4), {}),
    '2.0.0.8+cc81cee': ((2, 0, 0, '.', None, 8, 'cc81cee'), {}),
    '4.5.0.dev': ((4, 5, 0, '.', 'dev'), {}),
    '1.0.0.rc3': ((1, 0, 0, '.', 'rc', 3), {}),
    '1.0.1.dev0': ((1, 0, 1, '.', 'dev', 0), {}),
    '0.4.4.dev5+84e1d430': ((0, 4, 4, '.', 'dev', 5, '84e1d430'), {})}

NEW_KWARG_NAMES = ('major', 'minor', 'patch', 'pre_separator', 'pre_type', 'pre_patch', 'local')


class Tests(unittest.TestCase):

    def test_version_parse(self):
        for version_str, (args, kwargs) in CASES.items():
            version_tuple = tuple([
                args[i] if i < len(args)
                else (kwargs[KWARG_NAMES[i]] if KWARG_NAMES[i] in kwargs else None)
                for i in range(len(KWARG_NAMES))])
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


class TestsNew(unittest.TestCase):

    maxDiff = None

    def test_version_parse(self):
        for version_str, (args, kwargs) in NEW_CASES.items():
            version_tuple = tuple([
                args[i] if i < len(args)
                else (kwargs[NEW_KWARG_NAMES[i]] if NEW_KWARG_NAMES[i] in kwargs else None)
                for i in range(len(NEW_KWARG_NAMES))])
            with self.subTest(version_str=version_str, version_tuple=version_tuple):
                self.assertEqual(VersionNew.from_str(version_str).to_tuple(), version_tuple)
                try:
                    py_version = packaging.version.Version(version_str)
                except ValueError:
                    pass
                else:
                    if not (version_tuple[4] is not None and version_tuple[5] is None):
                        self.assertEqual(VersionNew.from_py_version(py_version).to_tuple(),
                                         version_tuple, py_version)
                try:
                    py_version_setuptools = pkg_resources.parse_version(version_str)
                except ValueError:
                    pass
                else:
                    if not (version_tuple[4] is not None and version_tuple[5] is None):
                        self.assertEqual(VersionNew.from_py_version(py_version_setuptools).to_tuple(),
                                         version_tuple, py_version_setuptools)
                try:
                    sem_version = semver.parse(version_str)
                except ValueError:
                    pass
                else:
                    self.assertEqual(VersionNew.from_sem_version(sem_version).to_tuple(),
                                     version_tuple, sem_version)
                try:
                    sem_version_info = semver.parse_version_info(version_str)
                except ValueError:
                    pass
                else:
                    self.assertEqual(VersionNew.from_sem_version(sem_version_info).to_tuple(),
                                     version_tuple, sem_version_info)

    def test_version_parse_bad(self):
        with self.assertRaises(ValueError):
            VersionNew.from_str('hello world')

    def test_version_generate(self):
        for result, (args, kwargs) in NEW_CASES.items():
            with self.subTest(args=args, kwargs=kwargs, result=result):
                self.assertEqual(VersionNew(*args, **kwargs).to_str(), result)

    def test_version_generate_bad(self):
        with self.assertRaises(TypeError):
            VersionNew().to_str()
        with self.assertRaises(ValueError):
            VersionNew(5, pre_patch=2).to_str()
        with self.assertRaises(ValueError):
            VersionNew(1, patch=13).to_str()
