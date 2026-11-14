"""Tests of local_version module."""

import logging
import unittest

from version_query.local_version import QUERIED, PREDICTED
from version_query.query import query_version_str, predict_version_str

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    def test_queried(self):
        _LOG.debug('QUERIED: %s', QUERIED)
        self.assertIsInstance(QUERIED, str)
        self.assertEqual(QUERIED, query_version_str())

    def test_predicted(self):
        _LOG.debug('PREDICTED: %s', PREDICTED)
        self.assertIsInstance(PREDICTED, str)
        self.assertEqual(PREDICTED, predict_version_str())
