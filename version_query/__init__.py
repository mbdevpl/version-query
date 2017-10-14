"""Package marker for version_query package."""

import logging
import os

if 'LOGGING_LEVEL' in os.environ:
    logging.basicConfig(level=getattr(logging, os.environ['LOGGING_LEVEL'].upper()))

from .query import query_version_str, predict_version_str
from .version import Version


def generate_version_str(increment_if_repo_chnaged: bool = True) -> str:
    """Generate the version string for current/upcoming version of the package."""
    import warnings
    warnings.warn('function generate_version_str() is deprecated, use predict() instead',
                  DeprecationWarning, stacklevel=2)
    from .query import predict_caller
    return predict_caller(2).to_str()
