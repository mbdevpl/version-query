"""Package marker for version_query package."""

import logging
import os

if 'LOGGING_LEVEL' in os.environ:
    logging.basicConfig(level=getattr(logging, os.environ['LOGGING_LEVEL'].upper()))

from .determine import determine_caller_version
from .increment import increment_caller_version
from .version import Version


def generate_version_str(increment_if_repo_chnaged: bool = True) -> str:
    if increment_if_repo_chnaged:
        try:
            return Version.generate_str(*increment_caller_version(2))
        except ValueError:
            pass
    return Version.generate_str(*determine_caller_version(2))
