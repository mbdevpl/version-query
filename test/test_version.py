"""Tests of version string parsing, generation and comparison."""

import logging
import unittest

import packaging.version
import pkg_resources
import semver

from version_query.version import VersionComponent, Version
from .examples import \
    INIT_CASES, BAD_INIT_CASES, COMPATIBLE_STR_CASES, STR_CASES, case_to_version_tuple, \
    INCREMENT_CASES, DEVEL_INCREMENT_CASES, COMPARISON_CASES_LESS, COMPARISON_CASES_EQUAL

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    maxDiff = None

    def test_from_str(self):
        for version_str, (args, kwargs) in STR_CASES.items():
            version_tuple = case_to_version_tuple(args, kwargs)
            with self.subTest(version_str=version_str, version_tuple=version_tuple):

                py_version = \
                    pkg_resources.parse_version(version_str)  # type: packaging.version.Version
                # self.assertIsInstance(
                #     py_version, packaging.version.Version, msg=(type(py_version), py_version))
                _LOG.debug('packaging parsed version string %s into %s: %s',
                           repr(version_str), type(py_version), py_version)

                try:
                    sem_version = semver.VersionInfo.parse(version_str)  # type: semver.VersionInfo
                except ValueError:
                    _LOG.debug('semver could not parse version string %s', repr(version_str))
                else:
                    _LOG.debug('semver parsed version string %s into %s: %s',
                               repr(version_str), type(sem_version), sem_version)

                self.assertEqual(Version.from_str(version_str).to_tuple(), version_tuple)

    def test_from_str_bad(self):
        with self.assertRaises(ValueError):
            Version.from_str('hello world')

    def test_to_str(self):
        for result, (args, kwargs) in STR_CASES.items():
            with self.subTest(args=args, kwargs=kwargs, result=result):
                self.assertEqual(Version(*args, **kwargs).to_str(), result)

    def test_from_py_version(self):
        for version_str, (args, kwargs) in COMPATIBLE_STR_CASES.items():
            version_tuple = case_to_version_tuple(args, kwargs)
            with self.subTest(version_str=version_str, version_tuple=version_tuple):
                py_version = packaging.version.Version(version_str)
                self.assertEqual(Version.from_py_version(py_version).to_tuple(),
                                 version_tuple, py_version)
                py_version_setuptools = pkg_resources.parse_version(version_str)
                self.assertEqual(Version.from_py_version(py_version_setuptools).to_tuple(),
                                 version_tuple, py_version_setuptools)

    def test_to_py_version(self):
        for version_str, (args, kwargs) in COMPATIBLE_STR_CASES.items():
            version_tuple = case_to_version_tuple(args, kwargs)
            with self.subTest(version_str=version_str, version_tuple=version_tuple):
                version = Version.from_str(version_str)
                py_version = packaging.version.Version(version_str)
                self.assertEqual(version.to_py_version(), py_version,
                                 msg=(version.to_py_version(), py_version))
                # py_version_setuptools = pkg_resources.parse_version(version_str)

    def test_from_sem_version(self):
        for version_str, (args, kwargs) in COMPATIBLE_STR_CASES.items():
            version_tuple = case_to_version_tuple(args, kwargs)
            with self.subTest(version_str=version_str, version_tuple=version_tuple):
                try:
                    sem_version = semver.VersionInfo.parse(version_str)  # type: semver.VersionInfo
                except ValueError:
                    continue
                else:
                    self.assertEqual(Version.from_sem_version(sem_version).to_tuple(),
                                     version_tuple, sem_version)
                sem_version_dict = sem_version.to_dict()
                self.assertEqual(Version.from_sem_version(sem_version_dict).to_tuple(),
                                 version_tuple, sem_version_dict)

    def test_to_sem_version(self):
        for version_str, (args, kwargs) in COMPATIBLE_STR_CASES.items():
            version_tuple = case_to_version_tuple(args, kwargs)
            with self.subTest(version_str=version_str, version_tuple=version_tuple):
                try:
                    sem_version = semver.VersionInfo.parse(version_str)
                except ValueError:
                    continue
                version = Version.from_str(version_str)
                self.assertEqual(version.to_sem_version(), sem_version)

    def test_from_version(self):
        for version_str, args_kwargs_tuple in INIT_CASES.items():
            args, kwargs = args_kwargs_tuple
            with self.subTest(args=args, kwargs=kwargs, version_str=version_str):
                version = Version.from_str(version_str)
                created_version = Version(*args, **kwargs)
                self.assertIsInstance(created_version, Version)
                self.assertEqual(version, created_version)
                version_copy = Version.from_version(created_version)
                self.assertEqual(version, version_copy)
                self.assertEqual(version_copy, created_version)

    def test_init(self):
        for version_str, args_kwargs_tuple in INIT_CASES.items():
            args, kwargs = args_kwargs_tuple
            with self.subTest(args=args, kwargs=kwargs, version_str=version_str):
                version = Version(*args, **kwargs)
                self.assertIsInstance(version, Version)
                self.assertEqual(Version.from_str(version_str), version)
                self.assertIsInstance(version.release, tuple)
                if version.pre_release is not None:
                    self.assertIsInstance(version.pre_release, list)
                if version.has_local:
                    self.assertIsInstance(version.local, tuple)

    def test_init_bad(self):
        for (args, kwargs), exception in BAD_INIT_CASES.items():
            with self.subTest(args=args, kwargs=kwargs, exception=exception):
                with self.assertRaises(exception):
                    Version(*args, **dict(kwargs))
        version = Version(1, 0)
        with self.assertRaises(TypeError):
            version.release = 2
        with self.assertRaises(ValueError):
            version.release = 2, 0
        with self.assertRaises(ValueError):
            version.release = 2, 0, 0, 1
        with self.assertRaises(ValueError):
            version.local = '42', 'and', '43'

    def test_increment(self):
        for (initial_version, args), result_version in INCREMENT_CASES.items():
            with self.subTest(initial_version=initial_version, args=args,
                              result_version=result_version):
                self.assertEqual(Version.from_str(initial_version).increment(*args),
                                 Version.from_str(result_version))

    def test_devel_increment(self):
        for (initial_version, args), result_version in DEVEL_INCREMENT_CASES.items():
            with self.subTest(initial_version=initial_version, args=args,
                              result_version=result_version):
                self.assertEqual(Version.from_str(initial_version).devel_increment(*args),
                                 Version.from_str(result_version))

    def test_increment_bad(self):
        version = Version(1, 0, 0)
        with self.assertRaises(TypeError):
            version.increment(3)
        with self.assertRaises(TypeError):
            version.increment('dev')
        with self.assertRaises(TypeError):
            version.increment(VersionComponent.Minor, '5')
        with self.assertRaises(ValueError):
            version.increment(VersionComponent.Minor, -1)
        with self.assertRaises(ValueError):
            version.increment(VersionComponent.Local)

    def test_compare(self):
        for earlier_version, later_version in COMPARISON_CASES_LESS.items():
            earlier = Version.from_str(earlier_version)
            later = Version.from_str(later_version)
            with self.subTest(earlier_version=earlier_version, later_version=later_version):
                self.assertLess(earlier, later)
                self.assertLessEqual(earlier, later)
                self.assertNotEqual(earlier, later)
                self.assertNotEqual(later, earlier)
                self.assertGreaterEqual(later, earlier)
                self.assertGreater(later, earlier)

        for version, equivalent_version in COMPARISON_CASES_EQUAL.items():
            original = Version.from_str(version)
            equivalent = Version.from_str(equivalent_version)
            with self.subTest(version=version, equivalent_version=equivalent_version):
                self.assertLessEqual(original, equivalent)
                self.assertLessEqual(equivalent, original)
                self.assertEqual(original, equivalent)
                self.assertEqual(equivalent, original)
                self.assertGreaterEqual(original, equivalent)
                self.assertGreaterEqual(equivalent, original)

    def test_compare_bad(self):
        with self.assertRaises(TypeError):
            assert Version(1, 0) < '2.0'

    def test_hash(self):
        for version, equivalent_version in COMPARISON_CASES_EQUAL.items():
            original = Version.from_str(version)
            equivalent = Version.from_str(equivalent_version)
            with self.subTest(version=version, equivalent_version=equivalent_version):
                self.assertEqual(hash(original), hash(equivalent))
                self.assertDictEqual({original: equivalent}, {equivalent: original})
