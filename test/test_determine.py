"""Tests of version determination functions."""

import pathlib
import runpy
import sys
import unittest

from version_query.determine import determine_version_from_git_repo, \
    determine_version_from_manifest, determine_caller_version


class Tests(unittest.TestCase):

    def test_my(self):
        version = determine_caller_version()
        self.assertIsInstance(version, tuple, type(version))
        self.assertEqual(len(version), 6, version)

    def test_git_repo(self):
        version = determine_version_from_git_repo(pathlib.Path.cwd())
        self.assertIsInstance(version, tuple, type(version))
        self.assertEqual(len(version), 6, version)

    def test_manifest(self):
        sys.argv = ['setup.py', 'sdist']
        runpy.run_module('setup', run_name='__main__')
        version = determine_version_from_manifest(pathlib.Path.cwd())
        self.assertIsInstance(version, tuple, type(version))
        self.assertEqual(len(version), 6, version)
