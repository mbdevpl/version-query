"""Initialization of tests of version_query package."""

import logging

from version_query.__main__ import Logging


class TestsLogging(Logging):
    """Logging configuration."""

    level_global = logging.DEBUG


TestsLogging.configure()
logging.getLogger('version_query.git_query').setLevel(logging.INFO)
logging.getLogger('version_query.parser').setLevel(logging.INFO)
logging.getLogger('version_query.version').setLevel(logging.INFO)
