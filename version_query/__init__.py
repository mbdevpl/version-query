"""Package marker for version_query package."""

from .version import VersionComponent, Version
from .query import query_folder, query_caller, query_version_str
from .git_query import predict_git_repo
from .query import predict_caller, predict_version_str


def generate_version_str(increment_if_repo_chnaged: bool = True) -> str:
    """Generate the version string for current/upcoming version of the package."""
    import warnings
    warnings.warn('function generate_version_str() is deprecated, use predict() instead',
                  DeprecationWarning, stacklevel=2)
    from .query import predict_caller
    return predict_caller(2).to_str()
