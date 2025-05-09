"""Tests of querying tools."""

import importlib
import logging
import os
import pathlib
import sys
import tempfile
import unittest

from boilerplates.packaging_tests import run_module

from version_query.version import Version
from version_query.git_query import query_git_repo, predict_git_repo
from version_query.py_query import query_metadata_json, query_pkg_info, query_package_folder
from version_query.query import query_folder, query_caller
from .examples import \
    PY_LIB_DIR, GIT_REPO_EXAMPLES, METADATA_JSON_EXAMPLE_PATHS, PKG_INFO_EXAMPLE_PATHS, \
    PACKAGE_FOLDER_EXAMPLES
from .test_cli import preserve_logger_level

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    def _check_examples_count(self, description, examples):
        lvl = logging.WARNING if len(examples) < 10 else logging.INFO
        _LOG.log(lvl, '%s count: %i', description, len(examples))
        if len(examples) < 5:
            _LOG.warning('%s list: %s', description, examples)
        self.assertGreater(len(examples), 0)

    def test_example_count_checking(self):
        _LOG.warning('%s', PY_LIB_DIR)

        with self.assertRaises(AssertionError):
            self._check_examples_count('test', [])
        self._check_examples_count('test', list(range(1)))
        self._check_examples_count('test', list(range(9)))
        self._check_examples_count('test', list(range(10)))

    def _query_test_case(self, paths, query_function):
        for path in paths:
            with self.subTest(path=path, query_function=query_function):
                _LOG.debug('testing %s() on %s', query_function.__name__, path)
                try:
                    version = query_function(path)
                except ValueError:
                    _LOG.info('failed to get version from %s', path, exc_info=True)
                else:
                    _LOG.debug('%s: %s', path, version)

    def test_query_git_repo(self):
        self._check_examples_count('git repo', GIT_REPO_EXAMPLES)
        self._query_test_case(GIT_REPO_EXAMPLES, query_git_repo)

    def test_predict_caller_bad(self):
        with tempfile.TemporaryDirectory() as project_path_str:
            with tempfile.NamedTemporaryFile(suffix='.py', dir=project_path_str,
                                             delete=False) as project_file:
                project_file_path = pathlib.Path(project_file.name)
            with project_file_path.open('a', encoding='utf-8') as project_file:
                project_file.write('from version_query.query import predict_caller\n\n\n'
                                   'def caller():\n    predict_caller()\n\n\ncaller()\n')
            sys.path.insert(0, project_path_str)
            _LOG.warning('inserted %s to sys.path', project_path_str)
            _LOG.info('temporary project file path: %s', project_file_path)
            with self.assertRaises(ValueError):
                importlib.import_module(project_file_path.with_suffix('').name)
            sys.path.remove(project_path_str)
            _LOG.warning('removed %s from sys.path', project_path_str)
            project_file_path.unlink()

    def test_predict_git_repo(self):
        self._query_test_case(GIT_REPO_EXAMPLES, predict_git_repo)

    @unittest.skipIf(not METADATA_JSON_EXAMPLE_PATHS, 'no "metadata.json" files found')
    def test_query_metadata_json(self):
        self._check_examples_count('metadata.json', METADATA_JSON_EXAMPLE_PATHS)
        self._query_test_case(METADATA_JSON_EXAMPLE_PATHS, query_metadata_json)

    @unittest.skipIf(not PKG_INFO_EXAMPLE_PATHS, 'no "PKG-INFO" files found')
    def test_query_pkg_info(self):
        self._check_examples_count('PKG-INFO', PKG_INFO_EXAMPLE_PATHS)
        self._query_test_case(PKG_INFO_EXAMPLE_PATHS, query_pkg_info)

    @unittest.skipUnless(
            os.environ.get('TEST_PACKAGING') or os.environ.get('CI'), 'skipping packaging test')
    def test_query_pkg_info_current(self):
        with preserve_logger_level('version_query'):
            run_module('setup', 'build')
        paths = list(pathlib.Path.cwd().glob('*.egg-info/PKG-INFO'))
        self.assertEqual(len(paths), 1)
        path = paths[0]
        version = query_pkg_info(path)
        _LOG.debug('%s: %s', path, version)

    def test_query_pkg_info_bad(self):
        with tempfile.NamedTemporaryFile(delete=False) as bad_file:
            bad_file_path = pathlib.Path(bad_file.name)
        with self.assertRaises(ValueError):
            query_pkg_info(bad_file_path)

        with bad_file_path.open('a', encoding='utf-8') as bad_file:
            bad_file.write('blah blah blah')
        with self.assertRaises(ValueError):
            query_pkg_info(bad_file_path)

        with bad_file_path.open('a', encoding='utf-8') as bad_file:
            bad_file.write('Version: hello world')
        with self.assertRaises(ValueError):
            query_pkg_info(bad_file_path)

        bad_file_path.unlink()

    def test_query_package_folder(self):
        self._check_examples_count('package folder', PACKAGE_FOLDER_EXAMPLES)
        self._query_test_case(PACKAGE_FOLDER_EXAMPLES, query_package_folder)

    @unittest.skipUnless(
            os.environ.get('TEST_PACKAGING') or os.environ.get('CI'), 'skipping packaging test')
    def test_query_package_folder_current(self):
        with preserve_logger_level('version_query'):
            run_module('setup', 'build')
        path = pathlib.Path.cwd().joinpath('version_query')
        version = query_package_folder(path)
        _LOG.debug('%s: %s', path, version)
        self.assertIsInstance(version, Version)

    def test_query_folder(self):
        self._query_test_case(PACKAGE_FOLDER_EXAMPLES, query_folder)

    def test_query_folder_current(self):
        path = pathlib.Path.cwd()
        version = query_folder(path)
        _LOG.debug('%s: %s', path, version)
        self.assertIsInstance(version, Version)

    def test_query_caller(self):
        version = query_caller()
        _LOG.debug('caller: %s', version)
        self.assertIsInstance(version, Version)
