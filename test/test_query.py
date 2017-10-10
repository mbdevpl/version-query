"""Tests of querying tools."""

import contextlib
import io
import logging
import os
import pathlib
import sys
import unittest

from version_query.version import VersionComponent
from version_query.git_query import query_git_repo
from version_query.py_query import query_metadata_json, query_pkg_info, query_package_folder
from version_query.query import query_folder, query_caller, predict_caller
from .examples import \
    GIT_REPO_EXAMPLES, METADATA_JSON_EXAMPLE_PATHS, PKG_INFO_EXAMPLE_PATHS, PACKAGE_FOLDER_EXAMPLES
from .test_setup import run_module

_LOG = logging.getLogger(__name__)


if sys.version_info < (3, 5):

    class _RedirectStream:

        _stream = None

        def __init__(self, new_target):
            self._new_target = new_target
            self._old_targets = []

        def __enter__(self):
            self._old_targets.append(getattr(sys, self._stream))
            setattr(sys, self._stream, self._new_target)
            return self._new_target

        def __exit__(self, exctype, excinst, exctb):
            setattr(sys, self._stream, self._old_targets.pop())

    class _redirect_stderr(_RedirectStream):

        _stream = "stderr"

    contextlib.redirect_stderr = _redirect_stderr


class Tests(unittest.TestCase):

    def test_deprecated(self):
        import warnings
        warnings.warn('remove this test after removing deprecated function',
                      DeprecationWarning, stacklevel=2)
        from version_query import generate_version_str
        with self.assertWarns(DeprecationWarning):
            generate_version_str()

    def test_examples(self):
        lvl = logging.WARNING if len(GIT_REPO_EXAMPLES) < 10 else logging.INFO
        _LOG.log(lvl, 'git repos count: %i', len(GIT_REPO_EXAMPLES))
        if len(GIT_REPO_EXAMPLES) < 5:
            _LOG.warning('git repos: %s', GIT_REPO_EXAMPLES)
        self.assertGreater(len(GIT_REPO_EXAMPLES), 0)

        lvl = logging.WARNING if len(METADATA_JSON_EXAMPLE_PATHS) < 10 else logging.INFO
        _LOG.log(lvl, 'metadata.json count: %i', len(METADATA_JSON_EXAMPLE_PATHS))
        if len(METADATA_JSON_EXAMPLE_PATHS) < 5:
            _LOG.warning('%s', METADATA_JSON_EXAMPLE_PATHS)
        self.assertGreater(len(METADATA_JSON_EXAMPLE_PATHS), 0)

        lvl = logging.WARNING if len(PKG_INFO_EXAMPLE_PATHS) < 10 else logging.INFO
        _LOG.log(lvl, 'PKG-INFO count: %i', len(PKG_INFO_EXAMPLE_PATHS))
        if len(PKG_INFO_EXAMPLE_PATHS) < 5:
            _LOG.warning('%s', PKG_INFO_EXAMPLE_PATHS)
        #self.assertGreater(len(PKG_INFO_EXAMPLE_PATHS), 0)

        lvl = logging.WARNING if len(PACKAGE_FOLDER_EXAMPLES) < 10 else logging.INFO
        _LOG.log(lvl, 'package folders: %i', len(PACKAGE_FOLDER_EXAMPLES))
        if len(PACKAGE_FOLDER_EXAMPLES) < 5:
            _LOG.warning('%s', PACKAGE_FOLDER_EXAMPLES)
        #self.assertGreater(len(PACKAGE_FOLDER_EXAMPLES), 0)

    def test_query_git_repo(self):
        for path in GIT_REPO_EXAMPLES:
            with self.subTest(path=path):
                try:
                    version = query_git_repo(path)
                    _LOG.debug('%s: %s', path, version)
                except ValueError:
                    _LOG.info('failed to get version from %s', path, exc_info=True)

    def test_query_metadata_json(self):
        for path in METADATA_JSON_EXAMPLE_PATHS:
            with self.subTest(path=path):
                try:
                    version = query_metadata_json(path)
                    _LOG.debug('%s: %s', path, version)
                except ValueError:
                    _LOG.exception('failed to get version from %s', path)

    def test_query_pkg_info(self):
        for path in PKG_INFO_EXAMPLE_PATHS:
            with self.subTest(path=path):
                try:
                    version = query_pkg_info(path)
                    _LOG.debug('%s: %s', path, version)
                except ValueError:
                    _LOG.exception('failed to get version from %s', path)

    @unittest.skipUnless(os.environ.get('TEST_PACKAGING'), 'skipping packaging test')
    def test_query_pkg_info_current(self):
        run_module('setup', 'build')
        paths = list(pathlib.Path.cwd().glob('*.egg-info/PKG-INFO'))
        self.assertEqual(len(paths), 1)
        path = paths[0]
        version = query_pkg_info(path)
        _LOG.debug('%s: %s', path, version)

    def test_query_package_folder(self):
        for path in PACKAGE_FOLDER_EXAMPLES:
            with self.subTest(path=path):
                try:
                    version = query_package_folder(path)
                    _LOG.debug('%s: %s', path, version)
                except ValueError:
                    _LOG.info('failed to get version from %s', path, exc_info=True)

    @unittest.skipUnless(os.environ.get('TEST_PACKAGING'), 'skipping packaging test')
    def test_query_package_folder_current(self):
        run_module('setup', 'build')
        path = pathlib.Path.cwd()
        version = query_package_folder(path)
        _LOG.debug('%s: %s', path, version)

    def test_query_folder(self):
        for path in PACKAGE_FOLDER_EXAMPLES:
            with self.subTest(path=path):
                try:
                    version = query_folder(path)
                    _LOG.debug('%s: %s', path, version)
                except ValueError:
                    _LOG.info('failed to get version from %s', path, exc_info=True)

    def test_query_folder_current(self):
        path = pathlib.Path.cwd()
        version = query_folder(path)
        _LOG.debug('%s: %s', path, version)

    def test_query_caller(self):
        version = query_caller()
        _LOG.debug('caller: %s', version)

    def test_not_as_main(self):
        run_module('version_query', run_name=None)

    def test_help(self):
        sio = io.StringIO()
        with contextlib.redirect_stderr(sio):
            with self.assertRaises(SystemExit):
                run_module('version_query')
        _LOG.info('%s', sio.getvalue())

    def test_here(self):
        sio = io.StringIO()
        with contextlib.redirect_stdout(sio):
            run_module('version_query', '.')
        self.assertEqual(sio.getvalue().rstrip(), query_caller().to_str())

    def test_increment_here(self):
        sio = io.StringIO()
        with contextlib.redirect_stdout(sio):
            run_module('version_query', '-i', '.')
        self.assertEqual(sio.getvalue().rstrip(),
                         query_caller().increment(VersionComponent.Patch).to_str())

    def test_predict_here(self):
        sio = io.StringIO()
        with contextlib.redirect_stdout(sio):
            run_module('version_query', '-p', '.')
        self.assertEqual(sio.getvalue().rstrip(), predict_caller().to_str())
