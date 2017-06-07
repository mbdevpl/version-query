"""Package marker for version_query package."""

from .determine import determine_version
from .version import Version


def generate_version_str():
    return Version.generate_str(*determine_version())
