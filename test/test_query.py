"""Tests of querying tools."""

import logging
import unittest

from version_query.git_query import query_git_repo
from version_query.py_query import query_metadata_json, query_pkg_info, query_package_folder
from version_query.query import query
from .examples import GIT_REPO_EXAMPLES, METADATA_JSON_EXAMPLE_PATHS, PKG_INFO_EXAMPLE_PATHS, PACKAGE_FOLDER_EXAMPLES

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    def test_examples(self):
        self.assertGreater(len(GIT_REPO_EXAMPLES), 0)
        _LOG.warning('git repos: %i', len(GIT_REPO_EXAMPLES))
        self.assertGreater(len(METADATA_JSON_EXAMPLE_PATHS), 0)
        _LOG.warning('metadata.json count: %i', len(METADATA_JSON_EXAMPLE_PATHS))
        self.assertGreater(len(PKG_INFO_EXAMPLE_PATHS), 0)
        _LOG.warning('PKG-INFO count: %i', len(PKG_INFO_EXAMPLE_PATHS))
        self.assertGreater(len(PACKAGE_FOLDER_EXAMPLES), 0)
        _LOG.warning('package folders: %i', len(PACKAGE_FOLDER_EXAMPLES))

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

    def test_query_package_folder(self):
        for path in PACKAGE_FOLDER_EXAMPLES:
            with self.subTest(path=path):
                try:
                    version = query_package_folder(path)
                    _LOG.debug('%s: %s', path, version)
                except ValueError:
                    _LOG.exception('failed to get version from %s', path)

    def test_query(self):
        for path in PACKAGE_FOLDER_EXAMPLES:
            with self.subTest(path=path):
                try:
                    version = query(path)
                    _LOG.debug('%s: %s', path, version)
                except ValueError:
                    _LOG.exception('failed to get version from %s', path)
