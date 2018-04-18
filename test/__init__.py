"""Tests for version_query package."""

import logging
import os

if 'LOGGING_LEVEL' in os.environ:
    logging.basicConfig(level=getattr(logging, os.environ['LOGGING_LEVEL'].upper()))
