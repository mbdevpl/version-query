"""Tests of version determination functions."""

import unittest

from version_query.determine import determine_version


class Tests(unittest.TestCase):

    def test_determine_version(self):
        version = determine_version()
        self.assertIsInstance(version, tuple, type(version))
        self.assertEqual(len(version), 6, version)
