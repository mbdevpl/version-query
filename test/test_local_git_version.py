"""Tests of local_git_version module."""

import logging

import unittest


from version_query.local_git_version import QUERIED, PREDICTED

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    def test_queried(self):
        _LOG.debug('QUERIED: %s', QUERIED)
        self.assertIsInstance(QUERIED, str)

    def test_predicted(self):
        _LOG.debug('PREDICTED: %s', PREDICTED)
        self.assertIsInstance(PREDICTED, str)
