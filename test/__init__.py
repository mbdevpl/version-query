"""Initialization of tests of version_query package."""

import logging

from version_query.__main__ import Logging


class TestsLogging(Logging):
    """Logging configuration."""

    level_package = logging.DEBUG


TestsLogging.configure()
