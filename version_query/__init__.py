"""Package marker for version_query package."""

import logging
import os

if 'LOGGING_LEVEL' in os.environ:
    logging.basicConfig(level=getattr(logging, os.environ['LOGGING_LEVEL'].upper()))

from .determine import determine_version
from .version import Version


def generate_version_str() -> str:
    return Version.generate_str(*determine_version())
